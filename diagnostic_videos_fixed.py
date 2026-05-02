"""
Diagnostic Videos Module - Fixed Version
Provides diagnostic videos for self-assessment
"""

DIAGNOSTIC_VIDEOS = {
    'neck_pain': {
        'en': {
            'title': '🎥 Neck Pain Self-Assessment Video',
            'videos': [
                {
                    'title': 'Neck Mobility Test',
                    'url': 'https://www.youtube.com/watch?v=neck_mobility_test',
                    'duration': '5 min',
                    'description': 'Simple tests to assess your neck mobility'
                },
                {
                    'title': 'Cervical Spine Assessment',
                    'url': 'https://www.youtube.com/watch?v=cervical_assessment',
                    'duration': '7 min',
                    'description': 'Professional cervical spine evaluation'
                }
            ]
        },
        'ar': {
            'title': '🎥 فيديو تقييم آلام الرقبة الذاتي',
            'videos': [
                {
                    'title': 'اختبار حركة الرقبة',
                    'url': 'https://www.youtube.com/watch?v=neck_mobility_ar',
                    'duration': '5 دقائق',
                    'description': 'اختبارات بسيطة لتقييم حركة رقبتك'
                },
                {
                    'title': 'تقييم العمود الفقري العنقي',
                    'url': 'https://www.youtube.com/watch?v=cervical_ar',
                    'duration': '7 دقائق',
                    'description': 'تقييم احترافي للعمود الفقري العنقي'
                }
            ]
        }
    },
    'shoulder_pain': {
        'en': {
            'title': '🎥 Shoulder Pain Self-Assessment Video',
            'videos': [
                {
                    'title': 'Shoulder Range of Motion Test',
                    'url': 'https://www.youtube.com/watch?v=shoulder_rom',
                    'duration': '6 min',
                    'description': 'Test your shoulder mobility and range'
                },
                {
                    'title': 'Rotator Cuff Assessment',
                    'url': 'https://www.youtube.com/watch?v=rotator_cuff',
                    'duration': '8 min',
                    'description': 'Check your rotator cuff strength'
                }
            ]
        },
        'ar': {
            'title': '🎥 فيديو تقييم آلام الكتف الذاتي',
            'videos': [
                {
                    'title': 'اختبار مدى حركة الكتف',
                    'url': 'https://www.youtube.com/watch?v=shoulder_ar',
                    'duration': '6 دقائق',
                    'description': 'اختبر مرونة كتفك ومداه'
                },
                {
                    'title': 'تقييم عضلات الكفة المدورة',
                    'url': 'https://www.youtube.com/watch?v=rotator_ar',
                    'duration': '8 دقائق',
                    'description': 'تحقق من قوة عضلات الكفة المدورة'
                }
            ]
        }
    },
    'lower_back_pain': {
        'en': {
            'title': '🎥 Lower Back Pain Self-Assessment Video',
            'videos': [
                {
                    'title': 'Lumbar Spine Mobility Test',
                    'url': 'https://www.youtube.com/watch?v=lumbar_mobility',
                    'duration': '7 min',
                    'description': 'Assess your lower back flexibility'
                },
                {
                    'title': 'Core Strength Assessment',
                    'url': 'https://www.youtube.com/watch?v=core_strength',
                    'duration': '8 min',
                    'description': 'Test your core stability and strength'
                }
            ]
        },
        'ar': {
            'title': '🎥 فيديو تقييم آلام أسفل الظهر الذاتي',
            'videos': [
                {
                    'title': 'اختبار حركة أسفل الظهر',
                    'url': 'https://www.youtube.com/watch?v=lumbar_ar',
                    'duration': '7 دقائق',
                    'description': 'قيّم مرونة أسفل ظهرك'
                },
                {
                    'title': 'تقييم قوة العضلات الأساسية',
                    'url': 'https://www.youtube.com/watch?v=core_ar',
                    'duration': '8 دقائق',
                    'description': 'اختبر استقرار وقوة عضلاتك الأساسية'
                }
            ]
        }
    },
    'knee_pain': {
        'en': {
            'title': '🎥 Knee Pain Self-Assessment Video',
            'videos': [
                {
                    'title': 'Knee Stability Test',
                    'url': 'https://www.youtube.com/watch?v=knee_stability',
                    'duration': '6 min',
                    'description': 'Check your knee stability and alignment'
                },
                {
                    'title': 'Knee Range of Motion Assessment',
                    'url': 'https://www.youtube.com/watch?v=knee_rom',
                    'duration': '7 min',
                    'description': 'Assess your knee flexibility'
                }
            ]
        },
        'ar': {
            'title': '🎥 فيديو تقييم آلام الركبة الذاتي',
            'videos': [
                {
                    'title': 'اختبار استقرار الركبة',
                    'url': 'https://www.youtube.com/watch?v=knee_ar',
                    'duration': '6 دقائق',
                    'description': 'تحقق من استقرار وتوازن ركبتك'
                },
                {
                    'title': 'تقييم مدى حركة الركبة',
                    'url': 'https://www.youtube.com/watch?v=knee_rom_ar',
                    'duration': '7 دقائق',
                    'description': 'قيّم مرونة ركبتك'
                }
            ]
        }
    }
}


def get_diagnostic_video(condition: str, language: str = 'English'):
    """Get diagnostic video for a condition"""
    lang_code = 'ar' if language == 'Arabic' else 'en'
    return DIAGNOSTIC_VIDEOS.get(condition, {}).get(lang_code)


def format_video_message(video_data: dict, language: str = 'English') -> str:
    """Format video message for Telegram"""
    if not video_data:
        return "No videos available" if language == 'English' else "لا توجد فيديوهات متاحة"
    
    title = video_data.get('title', '')
    videos = video_data.get('videos', [])
    
    message = f"{title}\n\n"
    
    for i, video in enumerate(videos, 1):
        message += f"{i}. **{video['title']}**\n"
        message += f"   ⏱️ {video['duration']}\n"
        message += f"   📝 {video['description']}\n"
        message += f"   🔗 [Watch Video]({video['url']})\n\n"
    
    return message
