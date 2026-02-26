"""
أدوات مساعدة للمهام
"""


class TaskUtils:
    """
    فئة مساعدة لمعالجة بيانات المهام
    """

    @staticmethod
    def validate_follow_up_input(task_name, date_follow, follow_up):
        """
        التحقق من صحة مدخلات المتابعة
        Args:
            task_name (str): اسم المهمة
            date_follow (str): تاريخ المتابعة
            follow_up (str): ملاحظات المتابعة
        Returns:
            dict: نتيجة التحقق
        """
        if not task_name or not date_follow or not follow_up:
            return {
                "status": "error",
                "message": "يجب ملء الحقول المطلوبة: task_name, date_follow, follow_up"
            }
        return {"status": "success"}

    @staticmethod
    def parse_progress(progress):
        """
        تحويل Progress إلى رقم صحيح بين 0-100
        Args:
            progress: قيمة التقدم
        Returns:
            int: قيمة التقدم بين 0-100
        """
        if not progress:
            return 0
        try:
            return max(0, min(100, int(progress)))
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def generate_summary(progress, date_follow, time_follow, follow_up):
        """
        توليد ملخص تحديث المهمة
        Args:
            progress (int): نسبة التقدم
            date_follow (str): تاريخ المتابعة
            time_follow (str): وقت المتابعة
            follow_up (str): ملاحظات المتابعة
        Returns:
            str: ملخص التحديث
        """
        time_part = f"{date_follow} {time_follow or ''}".strip()
        return f"{progress}% | {time_part} - {follow_up}"

    @staticmethod
    def generate_log_follow(task):
        """
        توليد سجل المتابعات من جدول child_follow
        Args:
            task (Document): وثيقة المهمة
        Returns:
            str: سجل المتابعات المنسق
        """
        rows = task.get("child_follow", []) or []
        
        if not rows:
            return ""
        
        # ترتيب تنازلي حسب التاريخ والوقت (الأحدث أولاً)
        sorted_rows = sorted(
            rows,
            key=lambda r: f"{r.get('date_follow') or ''} {r.get('time_follow') or ''}",
            reverse=True
        )
        
        lines = []
        for idx, row in enumerate(sorted_rows, 1):
            dt = f"{row.get('date_follow') or ''} {row.get('time_follow') or ''}".strip()
            reg = f" | Registered: {row.get('date_time_registration')}" if row.get('date_time_registration') else ""
            prog = f" | {row.get('progress')}%" if row.get('progress') else ""
            note = (row.get('follow_up') or "").replace("\n", " ")
            lines.append(f"{idx}) {dt}{reg}{prog}\n   - {note}")
        
        return "\n\n".join(lines)
