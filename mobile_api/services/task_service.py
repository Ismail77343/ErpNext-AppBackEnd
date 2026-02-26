import frappe
from mobile_api.repositories.task_repository import TaskRepository
from mobile_api.utils.task_utils import TaskUtils


class TaskService:
    """
    خدمات المهام - منطق العمل
    """

    @staticmethod
    def get_task_with_followers(task_name):
        """
        الحصول على تفاصيل المهمة مع المتابعات والأنشطة
        Args:
            task_name (str): اسم المهمة
        Returns:
            dict: بيانات المهمة الكاملة
        """
        task = TaskRepository.get_task(task_name)
        child_follow = TaskRepository.get_child_follow(task)
        activity_log = TaskRepository.get_activity_log(task_name)
        
        task_data = task.as_dict()
        task_data["child_follow"] = child_follow
        task_data["activity_log"] = activity_log
        return task_data

    @staticmethod
    def add_follow_up(task_name, date_follow, time_follow=None, progress=None, follow_up=None, attachment=None):
        """
        إضافة متابعة جديدة للمهمة
        Args:
            task_name (str): اسم المهمة
            date_follow (str): تاريخ المتابعة
            time_follow (str): وقت المتابعة
            progress (int): نسبة التقدم
            follow_up (str): ملاحظات المتابعة
            attachment (str): المرفقات
        Returns:
            dict: نتيجة العملية
        """
        # التحقق من المدخلات
        validation = TaskUtils.validate_follow_up_input(task_name, date_follow, follow_up)
        if validation["status"] == "error":
            return validation
        
        # التحقق من وجود المهمة
        if not TaskRepository.task_exists(task_name):
            return {
                "status": "error",
                "message": f"المهمة {task_name} غير موجودة"
            }
        
        task = TaskRepository.get_task(task_name)
        progress_value = TaskUtils.parse_progress(progress)
        
        # إضافة الصف الجديد
        TaskRepository.add_follow_up_row(task, date_follow, time_follow, progress_value, follow_up, attachment)
        
        # تحديث الملخص والسجل
        task.progress = progress_value
        task.last_update_summary = TaskUtils.generate_summary(progress_value, date_follow, time_follow, follow_up)
        task.log_follow = TaskUtils.generate_log_follow(task)
        
        TaskRepository.save_task(task)
        
        return {
            "status": "success",
            "message": "تم إضافة المتابعة بنجاح",
            "task_name": task.name,
            "progress": progress_value
        }

    @staticmethod
    def update_status(task_name, status):
        """
        تحديث حالة المهمة
        Args:
            task_name (str): اسم المهمة
            status (str): الحالة الجديدة
        Returns:
            dict: نتيجة العملية
        """
        task = TaskRepository.get_task(task_name)
        task.status = status
        TaskRepository.save_task(task)
        
        return {
            "status": "success",
            "message": f"تم تحديث حالة المهمة إلى {status}",
            "task_name": task.name,
            "current_status": task.status
        }
