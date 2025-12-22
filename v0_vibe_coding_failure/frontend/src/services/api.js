const API_BASE_URL = 'http://localhost:8000';

export async function calculateArcFlash(equipmentData) {
  const response = await fetch(`${API_BASE_URL}/api/v1/calculate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(equipmentData),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Calculation failed');
  }
  
  return response.json();
}

export async function calculateDetailed(equipmentData) {
  const response = await fetch(`${API_BASE_URL}/api/v1/calculate/detailed`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(equipmentData),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Calculation failed');
  }
  
  return response.json();
}