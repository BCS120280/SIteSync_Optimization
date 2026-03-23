SELECT                                                                                                                                          
      id,                                                                                                                                         
      device_id,                                                                                                                                  
      dev_eui,                                                                                                                                    
      installation_date,                                                                                                                          
      installer_user_id,                                                                                                                          
      installer_display_name                                                                                                                      
FROM installation_records                                                                                                                       
ORDER BY installation_date DESC                                                                                                                 
LIMIT :limit OFFSET :offset