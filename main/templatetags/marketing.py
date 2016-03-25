from django import template
register = template.Library()

@register.inclusion_tag('main/templatetags/circle_item.html')
def circle_header_item(img_name='marketing_0.png', heading='Test', caption='Test',
					   button_link="register", button_title="View details"):
	return {
		'img': img_name,
		'heading': heading,
		'caption': caption,
		'button_link': button_link,
		'button_title': button_title
	}
