from models.event import Event, event_registrations
from models.user import User
from models import db
from datetime import datetime, date, timedelta
from sqlalchemy import func, text, desc, and_, not_
from collections import defaultdict, Counter
import math

class RecommendationEngine:
    @staticmethod
    def get_user_recommendations(user, limit=5):
        """Get personalized event recommendations for a user"""
        try:
            all_recommendations = []
            
            # 1. Content-based recommendations (40% weight)
            content_recs = RecommendationEngine._content_based_filtering(user, limit)
            for rec in content_recs:
                rec['score'] = rec.get('score', 0) * 0.4
                all_recommendations.append(rec)
            
            # 2. Collaborative filtering (25% weight)
            collab_recs = RecommendationEngine._collaborative_filtering(user, limit)
            for rec in collab_recs:
                rec['score'] = rec.get('score', 0) * 0.25
                all_recommendations.append(rec)
            
            # 3. Popular/Trending events (20% weight)
            popular_recs = RecommendationEngine._popularity_based_filtering(user, limit)
            for rec in popular_recs:
                rec['score'] = rec.get('score', 0) * 0.2
                all_recommendations.append(rec)
            
            # 4. Diversity recommendations (15% weight)
            diversity_recs = RecommendationEngine._diversity_based_filtering(user, limit)
            for rec in diversity_recs:
                rec['score'] = rec.get('score', 0) * 0.15
                all_recommendations.append(rec)
            
            # Remove duplicates and sort by score
            seen_events = set()
            unique_recs = []
            
            for rec in sorted(all_recommendations, key=lambda x: x['score'], reverse=True):
                if rec['event'].id not in seen_events:
                    seen_events.add(rec['event'].id)
                    unique_recs.append(rec)
            
            # If we don't have enough recommendations, add fallback
            if len(unique_recs) < limit:
                fallback_recs = RecommendationEngine._fallback_recommendations(user, limit - len(unique_recs))
                for rec in fallback_recs:
                    if rec['event'].id not in seen_events:
                        unique_recs.append(rec)
            
            return unique_recs[:limit]
            
        except Exception as e:
            print(f"Recommendation error: {e}")
            return RecommendationEngine._fallback_recommendations(user, limit)
    
    @staticmethod
    def _content_based_filtering(user, limit):
        """Content-based filtering - includes similar categories and location-based"""
        user_events = user.registered_events
        if not user_events:
            return RecommendationEngine._fallback_recommendations(user, limit)
        
        # Get user's preferred categories
        category_counts = Counter([event.category for event in user_events])
        preferred_categories = list(category_counts.keys())
        
        # Get user's preferred locations
        location_counts = Counter([event.location for event in user_events])
        preferred_locations = list(location_counts.keys())
        
        recommendations = []
        
        # Get user's registered event IDs
        user_event_ids = [event.id for event in user_events]
        
        # 1. Same category recommendations
        for category in preferred_categories:
            same_category_events = Event.query.filter(
                Event.date >= date.today(),
                Event.category == category,
                not_(Event.id.in_(user_event_ids))
            ).all()
            
            for event in same_category_events:
                score = category_counts[category] / len(user_events)
                
                # Boost score for preferred locations
                if event.location in preferred_locations:
                    score *= 1.3
                
                # Boost score for events happening soon
                days_until = (event.date - date.today()).days
                if days_until <= 3:
                    score *= 1.8
                elif days_until <= 7:
                    score *= 1.5
                elif days_until <= 30:
                    score *= 1.2
                
                recommendations.append({
                    'event': event,
                    'score': score,
                    'reason': f"Based on your interest in {event.category} events"
                })
        
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)[:limit * 2]
    
    @staticmethod
    def _diversity_based_filtering(user, limit):
        """Recommend events from different categories to diversify user interests"""
        user_events = user.registered_events
        user_categories = set([event.category for event in user_events])
        user_event_ids = [event.id for event in user_events]
        
        # Get all available categories
        all_categories = db.session.query(Event.category).distinct().all()
        all_categories = [cat[0] for cat in all_categories]
        
        # Find categories user hasn't explored
        unexplored_categories = [cat for cat in all_categories if cat not in user_categories]
        
        recommendations = []
        
        # Recommend top events from unexplored categories
        for category in unexplored_categories:
            category_events = db.session.query(Event).filter(
                Event.date >= date.today(),
                Event.category == category,
                not_(Event.id.in_(user_event_ids))
            ).limit(2).all()
            
            for event in category_events:
                # Score based on popularity in that category
                reg_count = len(event.registered_users)
                popularity_score = min(reg_count / max(event.max_capacity, 1), 1.0)
                
                recommendations.append({
                    'event': event,
                    'score': popularity_score,
                    'reason': f"Explore {category} events - expand your interests!"
                })
        
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)[:limit]
    
    @staticmethod
    def _collaborative_filtering(user, limit):
        """Enhanced collaborative filtering"""
        user_events = set([e.id for e in user.registered_events])
        if not user_events:
            return []
        
        # Find users with at least one common event
        similar_users = []
        
        # Get all users who registered for at least one of the same events
        try:
            common_event_users = User.query.join(User.registered_events).filter(
                Event.id.in_(user_events),
                User.id != user.id
            ).distinct().all()
        except:
            return []
        
        for other_user in common_event_users:
            other_events = set([e.id for e in other_user.registered_events])
            if not other_events:
                continue
            
            # Calculate Jaccard similarity
            intersection = len(user_events & other_events)
            union = len(user_events | other_events)
            
            if union > 0:
                similarity = intersection / union
                if similarity > 0.1:  # Minimum threshold
                    similar_users.append((other_user, similarity))
        
        # Sort by similarity
        similar_users.sort(key=lambda x: x[1], reverse=True)
        
        # Get recommendations from similar users
        event_scores = defaultdict(float)
        event_reasons = {}
        
        for similar_user, similarity in similar_users[:5]:  # Top 5 similar users
            for event in similar_user.registered_events:
                if (event.id not in user_events and 
                    event.date >= date.today() and 
                    user not in event.registered_users):
                    
                    event_scores[event.id] += similarity
                    if event.id not in event_reasons:
                        event_reasons[event.id] = "Users with similar interests registered for this"
        
        recommendations = []
        for event_id, score in event_scores.items():
            event = Event.query.get(event_id)
            if event:
                recommendations.append({
                    'event': event,
                    'score': score,
                    'reason': event_reasons[event_id]
                })
        
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)[:limit]
    
    @staticmethod
    def _popularity_based_filtering(user, limit):
        """Enhanced popularity-based recommendations"""
        user_event_ids = [e.id for e in user.registered_events]
        
        # Build the query step by step
        query = db.session.query(
            Event,
            func.count(event_registrations.c.user_id).label('reg_count')
        ).outerjoin(event_registrations).filter(
            Event.date >= date.today()
        )
        
        # Add user event filter if user has registered events
        if user_event_ids:
            query = query.filter(not_(Event.id.in_(user_event_ids)))
        
        popular_events = query.group_by(Event.id).order_by(
            desc(func.count(event_registrations.c.user_id))
        ).limit(limit * 3).all()
        
        recommendations = []
        for event, reg_count in popular_events:
            # Calculate popularity score
            popularity_ratio = reg_count / max(event.max_capacity, 1)
            
            # Boost recent events
            days_until = (event.date - date.today()).days
            recency_factor = max(0.1, 1 - (days_until / 365))
            
            score = popularity_ratio * recency_factor
            
            recommendations.append({
                'event': event,
                'score': score,
                'reason': f"Popular event with {reg_count} registrations"
            })
        
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)[:limit]
    
    @staticmethod
    def _fallback_recommendations(user, limit):
        """Fallback recommendations when main algorithms fail"""
        user_event_ids = [e.id for e in user.registered_events]
        
        # Get upcoming events user hasn't registered for
        query = Event.query.filter(Event.start_date >= date.today())
        
        if user_event_ids:
            query = query.filter(not_(Event.id.in_(user_event_ids)))
        
        events = query.order_by(Event.start_date).limit(limit).all()
        
        return [{
            'event': event,
            'score': 0.1,
            'reason': 'Upcoming event you might be interested in'
        } for event in events]
    
    @staticmethod
    def get_trending_events(limit=10):
        """Get trending events based on recent registrations"""
        try:
            # Get events with registration counts from the last 7 days
            recent_date = date.today() - timedelta(days=7)
            
            trending = db.session.query(
                Event,
                func.count(event_registrations.c.user_id).label('registration_count')
            ).outerjoin(event_registrations).filter(
                Event.start_date >= date.today()
            ).group_by(Event.id).having(
                func.count(event_registrations.c.user_id) > 0
            ).order_by(
                desc(func.count(event_registrations.c.user_id))
            ).limit(limit).all()
            
            result = []
            for event, reg_count in trending:
                result.append({
                    'event': event,
                    'registration_count': reg_count
                })
            
            # If not enough trending events, add some popular upcoming events
            if len(result) < limit:
                additional_events = Event.query.filter(
                    Event.start_date >= date.today(),
                    not_(Event.id.in_([t['event'].id for t in result]))
                ).order_by(Event.start_date).limit(limit - len(result)).all()

                for event in additional_events:
                    result.append({
                        'event': event,
                        'registration_count': len(event.registered_users)
                    })
            
            return result
            
        except Exception as e:
            print(f"Error getting trending events: {e}")
            # Fallback: return upcoming events
            upcoming_events = Event.query.filter(
                Event.date >= date.today()
            ).order_by(Event.date).limit(limit).all()
            
            return [{'event': event, 'registration_count': len(event.registered_users)} 
                   for event in upcoming_events]

# Create a global instance for easy importing
def get_user_recommendations(user, limit=5):
    """Global function to get user recommendations"""
    return RecommendationEngine.get_user_recommendations(user, limit)

def get_trending_events(limit=10):
    """Global function to get trending events"""
    return RecommendationEngine.get_trending_events(limit)