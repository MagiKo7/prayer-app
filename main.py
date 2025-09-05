import requests
from datetime import datetime, timedelta
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

PRAYER_NAMES = {
    "Fajr": "الفجر",
    "Dhuhr": "الظهر",
    "Asr": "العصر",
    "Maghrib": "المغرب",
    "Isha": "العشاء"
}

def fetch_prayer_times(city, country):
    try:
        today = datetime.now().strftime("%d-%m-%Y")
        url = f"https://api.aladhan.com/v1/timingsByCity/{today}?city={city}&country={country}&method=5"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data and data['data']:
            return data['data']
    except:
        pass

    return {
        "timings": {
            "Fajr": "05:00",
            "Dhuhr": "12:00",
            "Asr": "15:30",
            "Maghrib": "18:00",
            "Isha": "19:30"
        },
        "date": {
            "readable": datetime.now().strftime("%d %b %Y"),
            "hijri": {
                "weekday": {"ar": "السبت"},
                "month": {"ar": "محرم"},
                "year": "1445",
                "day": "1"
            }
        }
    }

def get_next_prayer(timings):
    now = datetime.now()
    prayer_order = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']

    for prayer_key in prayer_order:
        if prayer_key not in timings:
            continue
        clean_time = timings[prayer_key].split()[0]
        hour, minute = map(int, clean_time.split(':'))
        prayer_datetime = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if prayer_datetime > now:
            return PRAYER_NAMES[prayer_key], prayer_datetime

    fajr_time_str = timings["Fajr"].split()[0]
    hour, minute = map(int, fajr_time_str.split(':'))
    next_prayer_time_dt = (now + timedelta(days=1)).replace(
        hour=hour, minute=minute, second=0, microsecond=0)
    return PRAYER_NAMES["Fajr"], next_prayer_time_dt

class PrayerApp(App):
    def build(self):
        self.city = "Bani Suwayf"
        self.country = "Egypt"
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.date_label = Label(text="", font_size=20, halign="center")
        self.layout.add_widget(self.date_label)
        self.hijri_label = Label(text="", font_size=18, halign="center")
        self.layout.add_widget(self.hijri_label)
        self.prayer_labels = {}
        for key, name in PRAYER_NAMES.items():
            lbl = Label(text=f"{name}: --:--", font_size=18)
            self.layout.add_widget(lbl)
            self.prayer_labels[key] = lbl
        self.countdown_label = Label(text="...", font_size=22, bold=True, halign="center")
        self.layout.add_widget(self.countdown_label)
        self.update_data()
        Clock.schedule_interval(self.update_countdown, 1)
        return self.layout

    def update_data(self, *args):
        self.prayer_data = fetch_prayer_times(self.city, self.country)
        if not self.prayer_data:
            return
        timings = self.prayer_data["timings"]
        hijri_date = self.prayer_data["date"]["hijri"]
        gregorian_date = self.prayer_data["date"]["readable"]
        self.date_label.text = f"التاريخ الميلادي: {gregorian_date}"
        self.hijri_label.text = f"التاريخ الهجري: {hijri_date['weekday']['ar']}، {hijri_date['day']} {hijri_date['month']['ar']} {hijri_date['year']} هـ"
        for prayer_key, lbl in self.prayer_labels.items():
            if prayer_key in timings:
                clean_time = timings[prayer_key].split()[0]
                lbl.text = f"{PRAYER_NAMES[prayer_key]}: {clean_time}"

    def update_countdown(self, *args):
        if not self.prayer_data:
            return
        next_prayer_name, next_prayer_time_dt = get_next_prayer(self.prayer_data["timings"])
        time_difference = next_prayer_time_dt - datetime.now()
        total_seconds = int(time_difference.total_seconds())
        if total_seconds < 0:
            self.countdown_label.text = "تحديث البيانات مطلوب"
            return
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        self.countdown_label.text = f"الصلاة القادمة: {next_prayer_name} خلال {hours:02d}:{minutes:02d}:{seconds:02d}"

if __name__ == "__main__":
    PrayerApp().run()
