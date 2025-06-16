 const API_KEY = '969f9fd68e54e135160a7f0e1f118155';

// Fungsi emoji cuaca
function weatherIcon(desc) {
    desc = desc.toLowerCase();
    if (desc.includes('rain')) return '🌧️';
    if (desc.includes('cloud')) return '☁️';
    if (desc.includes('clear')) return '☀️';
    if (desc.includes('snow')) return '❄️';
    if (desc.includes('storm') || desc.includes('thunder')) return '⛈️';
    return '🌥️';
}

// Fungsi memilih gif cuaca dari folder videos
function getWeatherGif(desc) {
    desc = desc.toLowerCase();
    if (desc.includes('rain')) return 'videos/hujan.gif';
    if (desc.includes('cloud')) return 'videos/mendung.gif';
    if (desc.includes('clear')) return 'videos/cerah.gif';
    if (desc.includes('storm') || desc.includes('thunder')) return 'videos/petir.gif';
    return 'videos/cerah.gif';
}

// Deteksi kota default via IP
function getLocationByIP() {
    fetch('https://ip-api.com/json')
    .then(res => res.json())
    .then(data => {
        document.getElementById('city-input').value = data.city || 'Lampung';
    })
    .catch(() => {
        document.getElementById('city-input').value = 'Lampung';
    });
}
getLocationByIP();

// Event handler
document.getElementById('weather-btn').onclick = showWeather;
document.getElementById('city-input').addEventListener("keypress", function(e) {
    if (e.key === "Enter") showWeather();
});

function showWeather() {
    const city = document.getElementById('city-input').value.trim();
    const unit = document.getElementById('unit-select').value;
    if (!city) {
        alert("Masukkan nama kota!");
        return;
    }
    // Bersihkan konten sebelumnya
    document.getElementById('weather-section').innerHTML = '';
    document.getElementById('alert-section').innerHTML = '';
    document.getElementById('hourly-section').innerHTML = '';
    document.getElementById('daily-section').innerHTML = '';

    const current_url = `https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(city)}&appid=${API_KEY}&units=${unit}&lang=id`;
    const forecast_url = `https://api.openweathermap.org/data/2.5/forecast?q=${encodeURIComponent(city)}&appid=${API_KEY}&units=${unit}&lang=id`;

    Promise.all([
        fetch(current_url).then(r => r.json()),
        fetch(forecast_url).then(r => r.json())
    ]).then(([current, forecast]) => {
        if (current.cod != 200) {
            document.getElementById('weather-section').innerHTML = `<div style="color:#f55;background:#fff3;padding:14px 10px;border-radius:8px;">Kota tidak ditemukan atau terjadi kesalahan pada API.</div>`;
            return;
        }
        // Data utama
        const weather = current.weather[0];
        const temp = Math.round(current.main.temp);
        const temp_max = Math.round(current.main.temp_max);
        const temp_min = Math.round(current.main.temp_min);
        const desc = weather.description.charAt(0).toUpperCase() + weather.description.slice(1);
        const icon = weatherIcon(weather.main);
        const degree_sign = unit === "metric" ? "°C" : "°F";
        const weatherGif = getWeatherGif(weather.main);

        // Weather card
        document.getElementById('weather-section').innerHTML = `
            <div class="weather-card">
                <div class="weather-card-content">
                    <div class="city-title">📍 ${city.charAt(0).toUpperCase()+city.slice(1)}</div>
                    <div class="temperature">${temp}${degree_sign}</div>
                    <div class="weather-desc">${desc} <span class="icon">${icon}</span></div>
                    <div class="temp-range">Tinggi: ${temp_max}${degree_sign} | Rendah: ${temp_min}${degree_sign}</div>
                </div>
            </div>
        `;

        // Atur background GIF setelah elemen tersedia di DOM
        setTimeout(() => {
            const cardContent = document.querySelector('.weather-card-content');
            if (cardContent) {
                cardContent.style.backgroundImage = `url('${weatherGif}')`;
                cardContent.style.backgroundPosition = 'center';
                cardContent.style.backgroundRepeat = 'no-repeat';
                cardContent.style.backgroundSize = 'cover';
            }
        }, 0);

        // Alert box
        document.getElementById('alert-section').innerHTML = `
            <div class='alert-box'>
                <strong>⚠️ Luapan Air Sungai</strong><br>
                Australian Government Bureau of Meteorology: Luapan Air Sungai di Molonglo River.
            </div>
        `;
        // Hourly forecast (next 6 x 3 jam)
        const next6 = forecast.list.slice(0,6);
        let hourlyHtml = `<div class="hourly"><h3>🌥️ Ramalan Per Jam (3 Jam Sekali)</h3>
            <div class="forecast-row">`;
        for (const hourData of next6) {
            const date = new Date(hourData.dt_txt);
            const jam = String(date.getHours()).padStart(2, '0') + ':00';
            const tempHour = Math.round(hourData.main.temp);
            const iconHour = weatherIcon(hourData.weather[0].main);
            hourlyHtml += `<div class="forecast-col">
                <div>${jam}</div>
                <div class="icon">${iconHour}</div>
                <div>${tempHour}${degree_sign}</div>
            </div>`;
        }
        hourlyHtml += '</div></div>';
        document.getElementById('hourly-section').innerHTML = hourlyHtml;

        // Daily forecast (5 hari ke depan)
        let daily = {};
        for (const fc of forecast.list) {
            const date = fc.dt_txt.slice(0,10);
            if (!daily[date]) {
                daily[date] = {
                    temp_min: fc.main.temp_min,
                    temp_max: fc.main.temp_max,
                    icon: fc.weather[0].main
                };
            } else {
                daily[date].temp_min = Math.min(daily[date].temp_min, fc.main.temp_min);
                daily[date].temp_max = Math.max(daily[date].temp_max, fc.main.temp_max);
            }
        }
        const dailyArr = Object.entries(daily).slice(0,5);
        let dailyHtml = `<div class="daily"><h3>☁️ Ramalan 5 Hari</h3>
            <div class="forecast-row">`;
        for (const [date, obj] of dailyArr) {
            const tgl = new Date(date);
            const hari = tgl.toLocaleDateString('id-ID', {weekday:'short', day:'2-digit', month:'short'});
            dailyHtml += `<div class="forecast-col">
                <div style="font-weight:bold">${hari}</div>
                <div class="icon-day">${weatherIcon(obj.icon)}</div>
                <div>${Math.round(obj.temp_max)}${degree_sign} / ${Math.round(obj.temp_min)}${degree_sign}</div>
            </div>`;
        }
        dailyHtml += '</div></div>';
        document.getElementById('daily-section').innerHTML = dailyHtml;

    }).catch(err => {
        document.getElementById('weather-section').innerHTML = `<div style="color:#f55;background:#fff3;padding:14px 10px;border-radius:8px;">Gagal mengambil data cuaca.</div>`;
    });
}
