  CREATE TABLE IF NOT EXISTS user_preferences (                                                                                                   
      id INTEGER PRIMARY KEY AUTOINCREMENT,                                                                                                       
      user_id TEXT NOT NULL,                                                                                                                      
      preference_key TEXT NOT NULL,                                                                                                               
      preference_value TEXT NOT NULL,                                                                                                             
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,                                                                                             
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,                                                                                             
      UNIQUE(user_id, preference_key)                                                                                                             
  );