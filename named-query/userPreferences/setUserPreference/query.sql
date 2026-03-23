INSERT INTO user_preferences (user_id, preference_key, preference_value, updated_at)                                                            
VALUES (:userId, :preferenceKey, :preferenceValue, CURRENT_TIMESTAMP)                                                                           
ON CONFLICT(user_id, preference_key)                                                                                                            
DO UPDATE SET preference_value = :preferenceValue, updated_at = CURRENT_TIMESTAMP