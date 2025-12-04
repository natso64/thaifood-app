def parse_thai_quantity(text):
    """
    แปลงข้อความปริมาณ (String) ให้เป็นตัวเลข (Float)
    รองรับรูปแบบ: '1/2', '3/4', '1+1/2', '1 1/2', '5'
    """
    if not isinstance(text, str):
        return float(text) if text else 0.0

    text = text.strip()

    try:
        # กรณี: มีเครื่องหมายบวก เช่น "1+1/2"
        if '+' in text:
            parts = text.split('+')
            return float(parts[0]) + parse_thai_quantity(parts[1])

        # กรณี: มีเว้นวรรค เช่น "1 1/2" (Mixed fraction)
        if ' ' in text:
            parts = text.split()
            # เช็คว่าส่วนหลังเป็นเศษส่วนหรือไม่
            if len(parts) == 2 and '/' in parts[1]:
                return float(parts[0]) + parse_thai_quantity(parts[1])

        # กรณี: เป็นเศษส่วน เช่น "1/2", "3/4"
        if '/' in text:
            num, den = text.split('/')
            return float(num) / float(den)

        # กรณี: ตัวเลขปกติ
        return float(text)

    except ValueError:
        return 0.0 # กรณีแปลงค่าไม่ได้