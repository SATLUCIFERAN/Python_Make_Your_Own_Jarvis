

from Chapter_9.Unit_Testing.jarvis_cli import calculate_power_output


def test_normal_operation():    
    temp = 80
    load = 0.5    
    result = calculate_power_output(temp, load)   
    assert result == 40.0

def test_emergency_shutdown():   
    temp = 100 
    result = calculate_power_output(temp, 0.8)    
    assert result == 0.0
    
