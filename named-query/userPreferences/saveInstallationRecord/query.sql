INSERT INTO installation_records                                                                                                                
      (device_id, dev_eui, installer_user_id, installer_display_name,                                                                             
       checklist_results, configuration_snapshot, health_metrics, updated_at)                                                                     
VALUES (:deviceId, :devEUI, :installerUserId, :installerDisplayName,                                                                            
          :checklistResults, :configurationSnapshot, :healthMetrics, CURRENT_TIMESTAMP)                                                           
ON CONFLICT(dev_eui) DO UPDATE SET                                                                                                              
      device_id = :deviceId,                                                                                                                      
      installer_user_id = :installerUserId,                                                                                                       
      installer_display_name = :installerDisplayName,                                                                                             
      checklist_results = :checklistResults,                                                                                                      
      configuration_snapshot = :configurationSnapshot,                                                                                            
      health_metrics = :healthMetrics,                                                                                                            
      installation_date = CURRENT_TIMESTAMP,                                                                                                      
      updated_at = CURRENT_TIMESTAMP