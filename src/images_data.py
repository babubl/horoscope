"""Freely licensed images from Wikimedia Commons (checked file pages: author and licence). Shown by hotlinking
Commons' Special:FilePath at a fixed width, with credit under each image."""
from urllib.parse import quote

# temple slug -> photo
TEMPLE = {
    'suryanar-kovil': dict(file='Suryanar Koil in Tamil Nadu JEG6875.jpg', author='PJeganathan', license='CC BY-SA 4.0'),
    'thingalur': dict(file='Kailasanathar Temple, Thingalur (5).jpg', author='Ssriram mt', license='CC BY-SA 4.0'),
    'vaitheeswaran-koil': dict(file='Vaitheeswarankovil5.JPG', author='Ssriram mt', license='CC BY-SA 4.0'),
    'thiruvenkadu': dict(file='Thiruvenkadu (5).jpg', author='Ssriram mt', license='CC BY-SA 4.0'),
    'alangudi': dict(file='Aalangudi Temple.jpg', author='Rasnaboy', license='CC BY-SA 3.0'),
    'kanjanur': dict(file='Kanjanur Sukkiran Temple.jpg', author='Sathiyaraj', license='CC BY-SA 4.0'),
    'thirunallar': dict(file='Thirunallar Dharbaranyeeswarar Temple and Tank.jpg', author='VasuVR', license='CC BY-SA 3.0'),
    'thirunageswaram': dict(file='Thirunageswaram gopuram.JPG', author='Rsmn', license='CC BY-SA 3.0'),
    'keezhaperumpallam': dict(file='Kethu sthal.JPG', author='Rsmn', license='CC BY-SA 3.0'),
    'thanjavur-big-temple': dict(file='Brihadisvara Temple during Maha Shivaratri-WUS03611 (edit).jpg', author='Rainer Halama (derivative: UnpetitproleX)', license='CC BY-SA 4.0'),
    'thirukadaiyur': dict(file='Thirukadayur (7).jpg', author='Ssriram mt', license='CC BY-SA 4.0'),
    'thirumanancheri': dict(file='Uthvanganathaswamy temple, Thirumananjeri (7).jpg', author='Ssriram mt', license='CC BY-SA 4.0', pos='center 25%'),
    'thirukarukavur': dict(file='Gopuram view from Temple tank.JPG', author='Selvamrpr', license='CC BY-SA 4.0'),
    'rameswaram': dict(file='Ramanathaswamy temple7.JPG', author='Ssriram mt', license='CC BY-SA 4.0', pos='center 30%'),
    'madurai-meenakshi': dict(file='Meenakshi Amman West Tower.jpg', author='KennyOMG', license='CC BY-SA 4.0'),
    'srirangam': dict(file='Ranganathaswamy temple tiruchirappalli.jpg', author='RUPESH MAURYA', license='CC BY-SA 4.0'),
}
# deity key -> public-domain painting
DEITY = {
    'shiva': dict(file='Siva-parvati-by-raja-ravi-varma.jpg', author='Raja Ravi Varma (attributed)', license='Public domain'),
    'meenakshi': dict(file='Siva-parvati-by-raja-ravi-varma.jpg', author='Raja Ravi Varma (attributed)', license='Public domain'),
    'murugan': dict(file='Murugan by Raja Ravi Varma.jpg', author='Raja Ravi Varma', license='Public domain'),
    'vishnu': dict(file='Raja Ravi Varma, Seshanarayana (Oleographic print).jpg', author='Raja Ravi Varma', license='Public domain'),
    'surya': dict(file='Surya Narayana.jpg', author='Ravi Varma Press', license='Public domain'),
    'navagraha': dict(file='Navagraha.jpg', author='Anant Shivaji Desai, Ravi Varma Press', license='Public domain'),
    'lakshmi': dict(file='Raja Ravi Varma, Goddess Lakshmi, 1896.jpg', author='Raja Ravi Varma', license='Public domain'),
}


def url(file, width=1280):
    name = file[5:] if file.startswith('File:') else file
    return f'https://commons.wikimedia.org/wiki/Special:FilePath/{quote(name.replace(" ", "_"))}?width={width}'


def page(file):
    name = file if file.startswith('File:') else 'File:' + file
    return 'https://commons.wikimedia.org/wiki/' + quote(name.replace(' ', '_'))
