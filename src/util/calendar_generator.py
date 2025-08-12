import calendar
import datetime
from io import BytesIO
import time

from PIL import Image, ImageDraw, ImageFont

font_title = ImageFont.truetype("src/fonts/MapleMono-Medium.ttf", 110)
font_day_number = ImageFont.truetype("src/fonts/MapleMono-Medium.ttf", 70)
font_day_str = ImageFont.truetype("src/fonts/MapleMono-Medium.ttf", 70)

img_mask = Image.open("src/images/mask2.png")

SQUARE_W = 128
SQUARE_DAY_SIZE = (SQUARE_W, SQUARE_W)

title_color = (255, 255, 0)

img_day_weekend_true = Image.new("RGB", SQUARE_DAY_SIZE, color=(135, 184, 205))
img_day_weekend_false = Image.new("RGB", SQUARE_DAY_SIZE, color=(11, 161, 112))
img_multibirthday_indicator = Image.new("RGB", SQUARE_DAY_SIZE, color=(112, 103, 110))

zone_day_str_y = 150

zone_days_x_init = 50
zone_days_y_init = 250

today_datetime = datetime.datetime.now()

month_str = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}

day_str = {0: "L", 1: "M", 2: "X", 3: "J", 4: "V", 5: "S", 6: "D"}


class CalendarGenerator:
    def new_calendar_img(self, month_int, bytes_dict):

        """
        bytes_dict = {
        
            7: [avatar1_bytes, avatar2_bytes],
            15: [avatar3_bytes]
        
        }
        
        
        
        """


        birthdays_number_by_day = [len(bytes_dict[y]) for y in bytes_dict.keys()]        
        # ^^^^^ esto es una lista que contiene la cantidad de avatares guardados segun los dias de ese mes
        

        multibirthday = sum(x>1 for x in birthdays_number_by_day) 
        # multibirthday sera igual al numero de dias en los que cumpla mas de una persona




        W, H = (1056+ multibirthday*138, 824)




        calendar.setfirstweekday(calendar.MONDAY)
        year_int = time.gmtime().tm_year
        day_relative_base = datetime.datetime(year_int, month_int, 1).weekday()
        a, total_days = calendar.monthrange(year_int, month_int)
        max_day_num = day_relative_base + total_days
        y = int(max_day_num / 7)

        x_inc = 138
        y_inc = 138

        img_base = Image.new("RGB", (W, H + y_inc), color=(62, 45, 82)) # fondo del calendario
        draw = ImageDraw.Draw(img_base)

        text_title = f"{month_str[month_int]}"

        xd1 = font_title.getbbox(text_title)
        w, h = xd1[2]-xd1[0], xd1[3]-xd1[1]
        draw.text(((W - w) / 2, 10), text_title, font=font_title, fill=(255, 255, 0))

        for i in range(7): # bucle para insertar las letras de los dias de la semana 
            day_name = day_str[i]
            xd2 = font_day_str.getbbox(day_name)

            w_d, h_d = xd2[2]-xd2[0], xd2[3]-xd2[1]

            pos_day_name_x = zone_days_x_init + i * x_inc + x_inc / 2 - w_d / 2

            draw.text(
                (pos_day_name_x, zone_day_str_y),
                day_name,
                font=font_day_str,
                fill=(255, 165, 0),
            )


        list_multibirthday=[]



        for num_day in range(1, total_days + 1): # bucle para ir insertando los dias con los numeros etc

            

            day_datetime = datetime.datetime(year_int, month_int, num_day)


            weekday = day_datetime.weekday() == 5 or day_datetime.weekday() == 6


            x = (day_relative_base + (num_day - 1)) % 7
            y = int((day_relative_base + (num_day - 1)) / 7)

            x_pos = zone_days_x_init + x * x_inc
            y_pos = zone_days_y_init + y * y_inc


            if weekday:
                img_base.paste(img_day_weekend_true, (x_pos, y_pos), img_mask)
            else:
                img_base.paste(img_day_weekend_false, (x_pos, y_pos), img_mask)



            if num_day in bytes_dict.keys(): # comprueba si alguien cumple ese dia
                if len(bytes_dict[num_day])==1:
                    img_avatar = Image.open(BytesIO(bytes_dict[num_day][0]))
                    img_base.paste(img_avatar, (x_pos, y_pos), img_mask)
                else: 
                    
                    list_multibirthday.append({num_day:len(bytes_dict[num_day])})
                    # ^^^^^ anoto cuales dias cumplen varias personas junto al numero de personas que cumplen

            else:
                xd3 = font_day_number.getbbox(str(num_day))
                size_day_number = [xd3[2]-xd3[0], xd3[3]-xd3[1]]
                pos_day_number_x = x_pos + SQUARE_W / 2 - size_day_number[0] / 2
                pos_day_number_y = y_pos + SQUARE_W / 2 - size_day_number[1] / 2

                pos_day_number = (pos_day_number_x, pos_day_number_y)


                if weekday:
                    draw.text(
                        pos_day_number,
                        str(num_day),
                        font=font_day_number,
                        fill=(112, 103, 110),
                    )
                else:
                    draw.text(
                        pos_day_number,
                        str(num_day),
                        font=font_day_number,
                        fill=(0, 255, 255),
                    )

            if (
                day_datetime.year == today_datetime.year
                and day_datetime.month == today_datetime.month
                and day_datetime.day == today_datetime.day
            ): # para marcar el dia actual
                rectangle_coord = (
                    x_pos - 5,
                    y_pos - 5,
                    x_pos + SQUARE_W + 5,
                    y_pos + SQUARE_W + 5,
                )
                draw.rounded_rectangle(
                    rectangle_coord, radius=18, fill=None, outline=(255, 0, 0), width=10
                )


        if multibirthday>0:

            x=7

            
            for col in range(multibirthday):
                x+=col # desplazamiento lateral
                y=0
                
                day=list(list_multibirthday[col].keys())[0]
                # list_multibirthday = [{8: 2}]
                for file in range(list_multibirthday[col][day]+1):
                    
                    
                    x_pos = zone_days_x_init + x * (x_inc+3)
                    y_pos = zone_days_y_init + y * y_inc
                    if file==0:
                        xd4 = font_day_number.getbbox(str(day))
                        size_day_number = [xd4[2]-xd4[0], xd4[3]-xd4[1]]
                        pos_day_number_x = x_pos + SQUARE_W / 2 - size_day_number[0] / 2
                        pos_day_number_y = y_pos + SQUARE_W / 2 - size_day_number[1] / 2
                        pos_day_number=(pos_day_number_x, pos_day_number_y)
                        img_base.paste(img_multibirthday_indicator, (x_pos, y_pos), img_mask)
                        draw.text(
                        pos_day_number,
                        str(day),
                        font=font_day_number,
                        fill=(0, 0, 0),
                        )
                    else:
                        img_avatar = Image.open(BytesIO(bytes_dict[day][file-1]))
                        img_base.paste(img_avatar, (x_pos, y_pos), img_mask)

                    y+=1


        output_buffer = BytesIO()
        img_base.save(output_buffer, "png")
        output_buffer.seek(0)

        return output_buffer