from django import forms
from datetime import date,datetime 
from job.models import Resume, Job


class DateInput(forms.DateInput):
    input_type = 'date'

class ResumeForm(forms.ModelForm):  

	class Meta:  
		model = Resume  
		fields =  ('first_name','last_name','state','email','mobile_no','degree','college','field_of_study','city','time_period_from','time_period_to','working_experince','job_title','company','company_city','experience_from','experience_to','desc','desired_job_title','desired_job_type','desired_salary','marks','image')
		widgets = {
          
			'time_period_from': DateInput(),
			'time_period_to': DateInput(),
			'experience_from': DateInput(),
			'experience_to': DateInput(),
        }


	def __init__(self, *args, **kwargs):
		super(ResumeForm, self).__init__(*args, **kwargs)
		self.fields['first_name'].widget.attrs = {'class': 'form-control',}
		self.fields['last_name'].widget.attrs = {'class': 'form-control',}
		self.fields['state'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['email'].widget.attrs = {'class': 'form-control',}
		self.fields['mobile_no'].widget.attrs = {'class': 'form-control',}
		self.fields['degree'].widget.attrs = {'class': 'form-control',}
		self.fields['college'].widget.attrs = {'class': 'form-control',}
		self.fields['field_of_study'].widget.attrs = {'class': 'form-control',}
		self.fields['city'].widget.attrs = {'class': 'form-control',}
		self.fields['time_period_from'].widget.attrs = {'class': 'form-control',}
		self.fields['time_period_to'].widget.attrs = {'class': 'form-control',}
		self.fields['working_experince'].widget.attrs = {'class': 'form-control',}
		self.fields['job_title'].widget.attrs = {'class': 'form-control',}
		self.fields['company'].widget.attrs = {'class': 'form-control',}
		self.fields['company_city'].widget.attrs = {'class': 'form-control',}
		self.fields['experience_from'].widget.attrs = {'class': 'form-control',}
		self.fields['experience_to'].widget.attrs = {'class': 'form-control',}
		self.fields['desc'].widget.attrs = {'class': 'form-control',}
		self.fields['desired_job_title'].widget.attrs = {'class': 'form-control',}
		self.fields['desired_job_type'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['desired_salary'].widget.attrs = {'class': 'form-control',}
		self.fields['marks'].widget.attrs = {'class': 'form-control',}


class JobPostForm(forms.ModelForm):  

	class Meta:  
		model = Job  
		fields =  ('job_title','location','job_function','employment_type','company_industry','seniority','job_desc','skills','image')
		widgets = {
          
			'time_period_from': DateInput(),
			'time_period_to': DateInput(),
			'experience_from': DateInput(),
			'experience_to': DateInput(),
        }


	def __init__(self, *args, **kwargs):
		super(JobPostForm, self).__init__(*args, **kwargs)
		
		self.fields['job_title'].widget.attrs = {'class': 'form-control',}
		self.fields['employment_type'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['job_function'].widget.attrs = {'class': 'form-control',}
		self.fields['location'].widget.attrs = {'class': 'form-control',}
		self.fields['company_industry'].widget.attrs = {'class': 'form-control',}
		self.fields['seniority'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['job_desc'].widget.attrs = {'class': 'form-control',}
		self.fields['skills'].widget.attrs = {'class': 'form-control',}
		

		
	

