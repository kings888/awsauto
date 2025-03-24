const i18n = {
    'zh': {
        'title': 'AWS EC2 实例创建',
        'instance_name': '实例名称',
        'region': 'AWS 区域',
        'volume_size': '硬盘大小 (GB)',
        'vpc_id': 'VPC ID',
        'need_public_ip': '是否需要公网 IP',
        'yes': '是',
        'no': '否',
        'instance_type': '实例类型',
        'owner': 'Owner',
        'team': 'Team',
        'application_name': 'Application Name',
        'environment': 'Environment',
        'create_instance': '创建实例',
        'creation_progress': '创建进度',
        'creation_success': '创建成功！',
        'instance_id': '实例 ID',
        'status': '状态',
        'public_ip': '公网 IP',
        'error': '错误'
    },
    'en': {
        'title': 'Create AWS EC2 Instance',
        'instance_name': 'Instance Name',
        'region': 'AWS Region',
        'volume_size': 'Volume Size (GB)',
        'vpc_id': 'VPC ID',
        'need_public_ip': 'Need Public IP',
        'yes': 'Yes',
        'no': 'No',
        'instance_type': 'Instance Type',
        'owner': 'Owner',
        'team': 'Team',
        'application_name': 'Application Name',
        'environment': 'Environment',
        'create_instance': 'Create Instance',
        'creation_progress': 'Creation Progress',
        'creation_success': 'Creation Successful!',
        'instance_id': 'Instance ID',
        'status': 'Status',
        'public_ip': 'Public IP',
        'error': 'Error'
    }
};

function getCurrentLanguage() {
    return localStorage.getItem('language') || 'zh';
}

function setLanguage(lang) {
    localStorage.setItem('language', lang);
    updatePageContent();
}

function updatePageContent() {
    const currentLang = getCurrentLanguage();
    const texts = i18n[currentLang];

    // Update title
    document.title = texts.title;
    document.querySelector('.card-header h3').textContent = texts.title;

    // Update form labels
    document.querySelector('label[for="instance_name"]').textContent = texts.instance_name;
    document.querySelector('label[for="region"]').textContent = texts.region;
    document.querySelector('label[for="volume_size"]').textContent = texts.volume_size;
    document.querySelector('label[for="vpc_id"]').textContent = texts.vpc_id;
    document.querySelector('label.form-label:nth-of-type(5)').textContent = texts.need_public_ip;
    document.querySelector('label[for="need_public_ip_true"]').textContent = texts.yes;
    document.querySelector('label[for="need_public_ip_false"]').textContent = texts.no;
    document.querySelector('label[for="instance_type"]').textContent = texts.instance_type;
    document.querySelector('label[for="owner"]').textContent = texts.owner;
    document.querySelector('label[for="team"]').textContent = texts.team;
    document.querySelector('label[for="application_name"]').textContent = texts.application_name;
    document.querySelector('label[for="environment"]').textContent = texts.environment;

    // Update button
    document.querySelector('button[type="submit"]').textContent = texts.create_instance;

    // Update result sections
    document.querySelector('#logSection h4').textContent = texts.creation_progress;
    document.querySelector('#resultSection h4').textContent = texts.creation_success;
    document.querySelector('#resultSection strong:nth-of-type(1)').textContent = texts.instance_id + '：';
    document.querySelector('#resultSection strong:nth-of-type(2)').textContent = texts.status + '：';
    document.querySelector('#publicIpSection strong').textContent = texts.public_ip + '：';

    // Update language switch button
    document.querySelector('#langSwitch').textContent = currentLang === 'zh' ? 'English' : '中文';
}