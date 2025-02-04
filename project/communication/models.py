from django.db import models
from django.utils.timezone import now
from cloudinary.models import CloudinaryField
from roomie_property.models import Property  # Import Property

class DamageRepairReport(models.Model):
    REPORT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]
    
    property = models.ForeignKey(Property, related_name='damage_reports', on_delete=models.CASCADE)
    tenant = models.ForeignKey('auth.User', related_name='damage_reports', on_delete=models.CASCADE)
    description = models.TextField(help_text="Describe the damage or repair needed.")
    status = models.CharField(max_length=15, choices=REPORT_STATUS_CHOICES, default='pending')
    reported_at = models.DateTimeField(default=now)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Report for {self.property} by {self.tenant.username} - Status: {self.status}"
    
    def mark_as_resolved(self):
        self.status = 'resolved'
        self.resolved_at = now()
        self.save()

    def mark_as_in_progress(self):
        self.status = 'in_progress'
        self.save()

    def mark_as_pending(self):
        self.status = 'pending'
        self.save()

class RepairImage(models.Model):
    damage_report = models.ForeignKey(
        DamageRepairReport, 
        related_name='repair_images', 
        on_delete=models.CASCADE,
        null=True,  # 🔥 Allow null values temporarily
        blank=True
    )
    image = CloudinaryField('image')
    description = models.CharField(max_length=255, blank=True, null=True)
