import frappe


class TaskRepository:
    """
    طبقة الوصول للبيانات - المهام
    """

    @staticmethod
    def get_task(task_name):
        """
        جلب وثيقة المهمة الكاملة
        Args:
            task_name (str): اسم المهمة
        Returns:
            Document: وثيقة المهمة
        """
        return frappe.get_doc("Task", task_name)

    @staticmethod
    def task_exists(task_name):
        """
        التحقق من وجود المهمة
        Args:
            task_name (str): اسم المهمة
        Returns:
            bool: True إذا كانت المهمة موجودة
        """
        return frappe.db.exists("Task", task_name)

    @staticmethod
    def get_child_follow(task):
        """
        جلب صفوف جدول المتابعة من المهمة
        Args:
            task (Document): وثيقة المهمة
        Returns:
            list: قائمة متابعات المهمة
        """
        child_rows = task.get("child_follow") or []
        return [row.as_dict() for row in child_rows]

    @staticmethod
    def get_activity_log(task_name):
        """
        جلب سجل الأنشطة والتعليقات على المهمة
        Args:
            task_name (str): اسم المهمة
        Returns:
            list: قائمة التعليقات والأنشطة
        """
        return frappe.get_list(
            "Comment",
            filters={"reference_doctype": "Task", "reference_name": task_name},
            fields=["name", "comment_by", "creation", "content"],
            order_by="creation desc"
        )

    @staticmethod
    def add_follow_up_row(task, date_follow, time_follow, progress, follow_up, attachment):
        """
        إضافة صف جديد في جدول المتابعة
        Args:
            task (Document): وثيقة المهمة
            date_follow (str): تاريخ المتابعة
            time_follow (str): وقت المتابعة
            progress (int): نسبة التقدم
            follow_up (str): ملاحظات المتابعة
            attachment (str): المرفقات (اختياري)
        """
        if hasattr(task, 'child_follow'):
            task.append('child_follow', {
                'date_follow': date_follow,
                'time_follow': time_follow or "",
                'date_time_registration': frappe.utils.now(),
                'follow_up': follow_up,
                'progress': progress,
                'file': attachment or ""
            })

    @staticmethod
    def save_task(task):
        """
        حفظ المهمة في قاعدة البيانات
        Args:
            task (Document): وثيقة المهمة المراد حفظها
        """
        task.save()
        frappe.db.commit()
