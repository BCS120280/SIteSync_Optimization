def calculate_signal_quality_score(rssi, snr, spreading_factor, environment_noise=0):
    """
    Calculate a radio signal strength quality score based on RSSI, SNR (adjusted by environmental noise), 
    and Spreading Factor.
    
    Args:
    rssi (float): Received Signal Strength Indicator in dBm.
    snr (float): Signal-to-Noise Ratio in dB.
    spreading_factor (int): LoRa Spreading Factor (typically between 6 and 12).
    environment_noise (float): Environmental noise level in dB to adjust the SNR (default is 0).
    
    Returns:
    float: A quality score ranging from 0 to 100, where 100 is the best quality.
    """
    
    # Normalize RSSI to a scale from 0 to 100
    # Assuming -120 dBm is the worst RSSI and -30 dBm is the best
    rssi_score = max(0, min(100, (rssi + 120) * 100 / 90))
    
    # Adjust SNR by environment noise and normalize to a scale from 0 to 100
    # Assuming -20 dB is the worst adjusted SNR and 20 dB is the best
    adjusted_snr = snr - environment_noise
    snr_score = max(0, min(100, (adjusted_snr + 20) * 100 / 40))
    
    # Normalize Spreading Factor to a scale from 0 to 100
    # Assuming SF12 is the worst (0 score) and SF7 is the best (100 score)
    sf_score = max(0, min(100, (12 - spreading_factor) * 100 / 5))
    
    # Compute the overall quality score as a weighted sum of the individual scores
    # Assigning weights (e.g., 0.5 for RSSI, 0.3 for SNR, 0.2 for SF)
    quality_score = (0.5 * rssi_score) + (0.3 * snr_score) + (0.2 * sf_score)
    
    return round(quality_score, 2)



def getBinnedColor(score):
	"""
    Categorizes a score into a color based on a scale from 0 to 100.
    
    Parameters:
    score (int or float): The score to categorize. Should be between 0 and 100.
    
    Returns:
    str: The color associated with the score.
    """
   	if not (0 <= score <= 100):
   		raise ValueError("Score must be between 0 and 100.")
    
	if score >= 80:
		return "#006B3E"
	elif score >= 50:
		return "#d4af37"
	elif score >= 20:
		return "#FF8C01"
	else:
		return "#ED2938"
		
		
def getClass(score):
	"""
    Categorizes a score into a color based on a scale from 0 to 100.
    
    Parameters:
    score (int or float): The score to categorize. Should be between 0 and 100.
    
    Returns:
    str: The color associated with the score.
    """
   	if not (0 <= score <= 100):
   		raise ValueError("Score must be between 0 and 100.")
    
	if score >= 80:
		return "Strong Signal"
	elif score >= 50:
		return "Average Sigal"
	elif score >= 20:
		return "Poor Signal"
	else:
		return "Bad Signal"