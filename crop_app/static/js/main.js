document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('mlChart').getContext('2d');

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Decision Tree', 'Naive Bayes', 'SVM', 'Logistic Regression', 'RF', 'XGBoost'],
            datasets: [
                {
                    label: 'Accuracy',
                    data: [87.5, 96.59, 95.45, 92.73, 96.59, 96.82],
                    backgroundColor: [
                        'rgb(255, 0, 0)',
                        'rgb(0, 0, 255)',
                        'rgb(60, 179, 113)',
                        'rgb(238, 130, 238)',
                        'rgb(255, 165, 0)',
                        'rgb(106, 90, 205)'
                    ],
                    borderColor: [
                        'black',
                        'black',
                        'black',
                        'black',
                        'black',
                        'black'
                    ],
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            animation: {
                duration: 2000,
                easing: 'easeInOutQuart'
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    titleFont: {
                        weight: '900',
                        family: "'Plus Jakarta Sans', 'Noto Sans', sans-serif"
                    },
                    bodyFont: {
                        weight: '900',
                        family: "'Plus Jakarta Sans', 'Noto Sans', sans-serif"
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        },
                        font: {
                            weight: '900',
                            family: "'Plus Jakarta Sans', 'Noto Sans', sans-serif"
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    title: {
                        display: true,
                        text: 'Accuracy (%)',
                        font: {
                            weight: '900',
                            family: "'Plus Jakarta Sans', 'Noto Sans', sans-serif"
                        }
                    }
                },
                x: {
                    ticks: {
                        font: {
                            weight: '900',
                            family: "'Plus Jakarta Sans', 'Noto Sans', sans-serif"
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    title: {
                        display: true,
                        text: 'ML Algorithms',
                        font: {
                            weight: '900',
                            family: "'Plus Jakarta Sans', 'Noto Sans', sans-serif"
                        }
                    }
                }
            }
        }
    });
});

// Add smooth animations to cards and metrics
const animateOnHover = (elements, transform) => {
    elements.forEach(element => {
        element.addEventListener('mouseenter', () => {
            element.style.transform = transform;
            element.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        });

        element.addEventListener('mouseleave', () => {
            element.style.transform = 'none';
        });
    });
};

// Initialize animations
document.addEventListener('DOMContentLoaded', () => {
    // Progress cards hover effect
    animateOnHover(document.querySelectorAll('.progress-card'), 'translateY(-8px)');
    
    // Environmental metrics hover effect
    animateOnHover(document.querySelectorAll('.env-metric'), 'translateY(-4px)');
    
    // Weather days hover effect
    animateOnHover(document.querySelectorAll('.weather-day'), 'translateX(4px)');
    
    // Add ripple effect to buttons
    document.querySelectorAll('button, .nav-item').forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = button.getBoundingClientRect();
            
            ripple.style.cssText = `
                position: absolute;
                background: rgba(255, 255, 255, 0.7);
                border-radius: 50%;
                pointer-events: none;
                width: 100px;
                height: 100px;
                transform: translate(-50%, -50%);
                animation: ripple 0.6s linear;
            `;
            
            ripple.style.left = e.clientX - rect.left + 'px';
            ripple.style.top = e.clientY - rect.top + 'px';
            
            button.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
});
// Replace with your own OpenWeatherMap API key
const API_KEY = 'f8ba931a56d6ea5d2ae125abe4a5b92a';
const CITY = 'Jatani';

async function fetchWeatherData() {
    const response = await fetch(
        `https://api.openweathermap.org/data/2.5/forecast?q=${CITY}&appid=${API_KEY}&units=metric`
    );
    const data = await response.json();
    displayWeatherData(data);
}

function getWeatherIcon(description) {
    // Define a mapping from weather descriptions to local icon file paths
    const baseUrl = '/static/images/';
    const icons = {
        'clear sky': `${baseUrl}partly-cloudy-removebg-preview.png`,
        'few clouds': `${baseUrl}partly-cloudy-removebg-preview.png`,
        'scattered clouds': `${baseUrl}cloudy-removebg-preview.png`,
        'broken clouds': `${baseUrl}cloudy-removebg-preview.png`,
        'shower rain': `${baseUrl}rainy.webp`,
        'rain': `${baseUrl}rainy.webp`,
        'thunderstorm': `${baseUrl}thunderstorm.png`,
        'snow': `${baseUrl}cloudy-removebg-preview.png`,
        'mist': `${baseUrl}cloudy-removebg-preview.png`,
        'sunny': `${baseUrl}sunny.png`,
        'light rain' : `${baseUrl}rainy.webp`,
    };

    // Return the corresponding icon or a default icon if no match is found
    return icons[description] || `${baseUrl}default.png`;
}
function displayWeatherData(data) {
    const weatherCardsContainer = document.getElementById('weather-cards');
    weatherCardsContainer.innerHTML = ''; // Clear any existing cards

    const currentDate = new Date();
    
    // Get the first forecast entry for today
    const currentDayData = data.list.find(item => {
        const itemDate = new Date(item.dt * 1000);
        return itemDate.toDateString() === currentDate.toDateString();
    });

    if (currentDayData) {
        const currentTemp = Math.round(currentDayData.main.temp);
        const currentDescription = currentDayData.weather[0].description;
        const currentIconPath = getWeatherIcon(currentDescription);

        // Create a card for the current day's weather
        const currentDayCard = document.createElement('div');
        currentDayCard.className = 'weather-card';
        currentDayCard.innerHTML = `
            <h3>Today</h3>
            <img src="${currentIconPath}" alt="${currentDescription}">
            <p>${currentTemp}°C</p>
        `;
        weatherCardsContainer.appendChild(currentDayCard);
    }

    const dailyData = data.list
        .filter(item => {
            const itemDate = new Date(item.dt * 1000);
            return itemDate > currentDate && item.dt_txt.includes('12:00:00');
        })
        .slice(1,5); 

    // Check if dailyData is populated
    console.log(data.list);

    dailyData.forEach(day => {
        const date = new Date(day.dt * 1000);
        const formattedDate = date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });

        const temp = Math.round(day.main.temp);
        const description = day.weather[0].description;

        // Get the local icon based on the weather description
        const iconPath = getWeatherIcon(description);

        const card = document.createElement('div');
        card.className = 'weather-card';
        card.innerHTML = `
            <h3>${formattedDate}</h3>
            <img src="${iconPath}" alt="${description}">
            <p>${temp}°C</p>
        `;
        weatherCardsContainer.appendChild(card);
    });
}



// Fetch weather data when the page loads
window.onload = fetchWeatherData;
