SELECT                                                                                                                                          
      id,                                                                                                                                         
      device_id,                                                                                                                                  
      dev_eui,                                                                                                                                    
      installation_date,                                                                                                                          
      installer_user_id,                                                                                                                          
      installer_display_name,                                                                                                                     
      checklist_results,                                                                                                                          
      configuration_snapshot,                                                                                                                     
      health_metrics,                                                                                                                             
      photo_path                                                                                                                                  
FROM installation_records                                                                                                                       
WHERE dev_eui = :devEUI