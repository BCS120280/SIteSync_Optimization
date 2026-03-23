SELECT preference_value                                                                                                                         
FROM user_preferences                                                                                                                           
WHERE user_id = :userId AND preference_key = :preferenceKey