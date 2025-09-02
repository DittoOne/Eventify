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
            print(f"DEBUG: Getting recommendations for user: {user.username}")
            
            # Get user's registered events
            user_events = user.registered_events
            user_event_ids = [e.id for e in user_events]
            
            print(f"DEBUG: User has registered for {len(user_events)} events")
            print(f"DEBUG: User event IDs: {user_event_ids}")
            
            if not user_events:
                print("DEBUG: User has no registered events, using fallback recommendations")
                return RecommendationEngine._fallback_recommendations(user, limit)
            
            all_recommendations = []
            
            # 1. Content-based recommendations (50% weight)
            content_recs = RecommendationEngine._content_based_filtering(user, limit * 2)
            print(f"DEBUG: Content-based found {len(content_recs)} recommendations")
            for rec in content_recs:
                rec['score'] = rec.get('score', 0) * 0.5
                all_recommendations.append(rec)
            
            # 2. Collaborative filtering (25% weight)
            collab_recs = RecommendationEngine._collaborative_filtering(user, limit)
            print(f"DEBUG: Collaborative filtering found {len(collab_recs)} recommendations")
            for rec in collab_recs:
                rec['score'] = rec.get('score', 0) * 0.25
                all_recommendations.append(rec)
            
            # 3. Popular/Trending events (25% weight)
            popular_recs = RecommendationEngine._popularity_based_filtering(user, limit)
            print(f"DEBUG: Popularity-based found {len(popular_recs)} recommendations")
            for rec in popular_recs:
                rec['score'] = rec.get('score', 0) * 0.25
                all_recommendations.append(rec)
            
            # Remove duplicates and sort by score
            seen_events = set()
            unique_recs = []
            
            for rec in sorted(all_recommendations, key=lambda x: x['score'], reverse=True):
                if rec['event'].id not in seen_events:
                    seen_events.add(rec['event'].id)
                    unique_recs.append(rec)
                    print(f"DEBUG: Added unique rec: {rec['event'].title} - Score: {rec['score']:.3f}")
            
            print(f"DEBUG: Final unique recommendations: {len(unique_recs)}")
            
            # If we don't have enough recommendations, add fallback
            if len(unique_recs) < limit:
                fallback_needed = limit - len(unique_recs)
                print(f"DEBUG: Need {fallback_needed} fallback recommendations")
                fallback_recs = RecommendationEngine._fallback_recommendations(user, fallback_needed, exclude_ids=seen_events)
                unique_recs.extend(fallback_recs)
            
            return unique_recs[:limit]
            
        except Exception as e:
            print(f"DEBUG: Recommendation error: {e}")
            import traceback
            traceback.print_exc()
            return RecommendationEngine._fallback_recommendations(user, limit)
    
    @staticmethod
    def _content_based_filtering(user, limit):
        """Improved content-based filtering using start_date"""
        user_events = user.registered_events
        if not user_events:
            return []
        
        # Get user's registered event IDs
        user_event_ids = [event.id for event in user_events]
        
        # Analyze user preferences
        category_counts = Counter([event.category for event in user_events])
        location_counts = Counter([event.location for event in user_events])
        
        print(f"DEBUG: User categories: {dict(category_counts)}")
        print(f"DEBUG: User locations: {dict(location_counts)}")
        
        # Get upcoming events user hasn't registered for
        available_events = Event.query.filter(
            Event.start_date >= date.today(),
            not_(Event.id.in_(user_event_ids))
        ).all()
        
        print(f"DEBUG: Found {len(available_events)} available events for content filtering")
        
        recommendations = []
        
        for event in available_events:
            score = 0.0
            reasons = []
            
            # Category preference scoring (most important factor)
            if event.category in category_counts:
                category_preference = category_counts[event.category] / len(user_events)
                category_score = category_preference * 0.8  # Strong weight for category match
                score += category_score
                reasons.append(f"matches your interest in {event.category} events")
                print(f"DEBUG: Event {event.title} - Category '{event.category}' score: {category_score:.3f}")
            
            # Location preference scoring
            if event.location in location_counts:
                location_preference = location_counts[event.location] / len(user_events)
                location_score = location_preference * 0.3
                score += location_score
                reasons.append(f"at your preferred location")
                print(f"DEBUG: Event {event.title} - Location score: {location_score:.3f}")
            
            # Time-based scoring (prefer events happening soon)
            days_until = (event.start_date - date.today()).days
            if days_until <= 3:
                time_boost = 0.4
                reasons.append("happening very soon")
            elif days_until <= 7:
                time_boost = 0.3
                reasons.append("happening this week")
            elif days_until <= 30:
                time_boost = 0.2
                reasons.append("happening this month")
            else:
                time_boost = 0.1
            
            score += time_boost
            
            # Availability scoring
            if hasattr(event, 'max_capacity') and event.max_capacity > 0:
                registered_count = len(event.registered_users)
                availability_ratio = (event.max_capacity - registered_count) / event.max_capacity
                if availability_ratio > 0.8:
                    score += 0.15
                    reasons.append("has excellent availability")
                elif availability_ratio > 0.5:
                    score += 0.1
                    reasons.append("has good availability")
            
            # Only include events with meaningful scores
            if score > 0.1:
                reason_text = "Recommended because it " + " and ".join(reasons) if reasons else "Based on your activity"
                recommendations.append({
                    'event': event,
                    'score': min(score, 1.0),  # Cap at 1.0
                    'reason': reason_text
                })
                print(f"DEBUG: Content-based added {event.title} with score {score:.3f}")
        
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)[:limit]
    
    @staticmethod
    def _collaborative_filtering(user, limit):
        """Find users with similar preferences and recommend their events"""
        user_event_ids = set([e.id for e in user.registered_events])
        if not user_event_ids:
            return []
        
        print(f"DEBUG: Starting collaborative filtering")
        
        try:
            # Find users who registered for at least one common event
            similar_users_data = []
            
            # Get all users who have registered for events
            all_users = User.query.join(User.registered_events).filter(
                User.id != user.id
            ).distinct().all()
            
            print(f"DEBUG: Found {len(all_users)} other users to compare")
            
            for other_user in all_users:
                other_event_ids = set([e.id for e in other_user.registered_events])
                if not other_event_ids:
                    continue
                
                # Calculate Jaccard similarity
                intersection = len(user_event_ids & other_event_ids)
                union = len(user_event_ids | other_event_ids)
                
                if intersection > 0 and union > 0:
                    similarity = intersection / union
                    if similarity > 0.1:  # Minimum similarity threshold
                        similar_users_data.append((other_user, similarity, intersection))
                        print(f"DEBUG: Found similar user {other_user.username} with similarity {similarity:.3f}")
            
            # Sort by similarity
            similar_users_data.sort(key=lambda x: x[1], reverse=True)
            
            # Get recommendations from similar users
            event_scores = defaultdict(float)
            event_objects = {}
            
            for other_user, similarity, common_events in similar_users_data[:10]:  # Top 10 similar users
                for event in other_user.registered_events:
                    if (event.id not in user_event_ids and 
                        event.start_date >= date.today()):
                        
                        # Weight by similarity and number of common events
                        weight = similarity * (1 + math.log(common_events))
                        event_scores[event.id] += weight
                        event_objects[event.id] = event
                        print(f"DEBUG: Collaborative rec: {event.title} += {weight:.3f}")
            
            recommendations = []
            for event_id, score in sorted(event_scores.items(), key=lambda x: x[1], reverse=True):
                event = event_objects[event_id]
                recommendations.append({
                    'event': event,
                    'score': min(score, 1.0),
                    'reason': f"Users with similar interests also registered for this event"
                })
            
            return recommendations[:limit]
            
        except Exception as e:
            print(f"DEBUG: Collaborative filtering error: {e}")
            return []
    
    @staticmethod
    def _popularity_based_filtering(user, limit):
        """Recommend popular events user hasn't registered for"""
        user_event_ids = [e.id for e in user.registered_events]
        
        try:
            # Get events with registration counts
            popular_events = db.session.query(
                Event,
                func.count(event_registrations.c.user_id).label('reg_count')
            ).outerjoin(event_registrations).filter(
                Event.start_date >= date.today(),
                not_(Event.id.in_(user_event_ids)) if user_event_ids else True
            ).group_by(Event.id).order_by(
                desc(func.count(event_registrations.c.user_id))
            ).limit(limit * 2).all()
            
            recommendations = []
            for event, reg_count in popular_events:
                # Calculate popularity score
                if hasattr(event, 'max_capacity') and event.max_capacity > 0:
                    popularity_ratio = reg_count / event.max_capacity
                else:
                    popularity_ratio = min(reg_count / 50, 1.0)  # Assume 50 as average capacity
                
                # Boost recent events
                days_until = (event.start_date - date.today()).days
                recency_factor = max(0.3, 1 - (days_until / 90))  # 90-day decay
                
                score = popularity_ratio * recency_factor
                
                recommendations.append({
                    'event': event,
                    'score': min(score, 1.0),
                    'reason': f"Popular event with {reg_count} registrations"
                })
                print(f"DEBUG: Popular event {event.title} - {reg_count} registrations, score: {score:.3f}")
            
            return sorted(recommendations, key=lambda x: x['score'], reverse=True)[:limit]
            
        except Exception as e:
            print(f"DEBUG: Popularity filtering error: {e}")
            return []
    
    @staticmethod
    def _fallback_recommendations(user, limit, exclude_ids=None):
        """Fallback recommendations when main algorithms fail"""
        if exclude_ids is None:
            exclude_ids = set()
        
        user_event_ids = [e.id for e in user.registered_events]
        all_exclude_ids = set(user_event_ids) | exclude_ids
        
        print(f"DEBUG: Fallback recommendations, excluding {len(all_exclude_ids)} events")
        
        # Get upcoming events user hasn't registered for
        query = Event.query.filter(Event.start_date >= date.today())
        
        if all_exclude_ids:
            query = query.filter(not_(Event.id.in_(list(all_exclude_ids))))
        
        events = query.order_by(Event.start_date).limit(limit).all()
        
        print(f"DEBUG: Fallback found {len(events)} events")
        
        return [{
            'event': event,
            'score': 0.1,
            'reason': 'Upcoming event you might find interesting'
        } for event in events]
    
    @staticmethod
    def get_trending_events(limit=10):
        """Get trending events based on recent registrations"""
        try:
            print(f"DEBUG: Getting trending events")
            
            # Get events with registration counts
            trending = db.session.query(
                Event,
                func.count(event_registrations.c.user_id).label('registration_count')
            ).outerjoin(event_registrations).filter(
                Event.start_date >= date.today()
            ).group_by(Event.id).having(
                func.count(event_registrations.c.user_id) >= 0  # Include all events
            ).order_by(
                desc(func.count(event_registrations.c.user_id)),
                Event.start_date
            ).limit(limit).all()
            
            result = []
            for event, reg_count in trending:
                result.append({
                    'event': event,
                    'registration_count': reg_count
                })
                print(f"DEBUG: Trending event: {event.title} - {reg_count} registrations")
            
            return result
            
        except Exception as e:
            print(f"DEBUG: Error getting trending events: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback: return upcoming events
            upcoming_events = Event.query.filter(
                Event.start_date >= date.today()
            ).order_by(Event.start_date).limit(limit).all()
            
            return [{'event': event, 'registration_count': len(event.registered_users)} 
                   for event in upcoming_events]

# Global functions for easy importing
def get_user_recommendations(user, limit=5):
    """Global function to get user recommendations"""
    return RecommendationEngine.get_user_recommendations(user, limit)

def get_trending_events(limit=10):
    """Global function to get trending events"""
    return RecommendationEngine.get_trending_events(limit)