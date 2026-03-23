  CREATE TABLE IF NOT EXISTS installation_records (                                                                                               
      id INTEGER PRIMARY KEY AUTOINCREMENT,                                                                                                       
      device_id TEXT NOT NULL,                                                                                                                    
      dev_eui TEXT NOT NULL,                                                                                                                      
      installation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,                                                                                      
      installer_user_id TEXT NOT NULL,                                                                                                            
      installer_display_name TEXT,                                                                                                                
      checklist_results TEXT NOT NULL,                                                                                                            
      configuration_snapshot TEXT NOT NULL,                                                                                                       
      health_metrics TEXT,                                                                                                                        
      photo_path TEXT,                                                                                                                            
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,                                                                                             
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,                                                                                             
      UNIQUE(dev_eui)                                                                                                                             
  );