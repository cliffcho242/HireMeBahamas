/**
 * Smart Search Algorithm for HireBahamas
 * Provides intelligent job/service/people search with fuzzy matching,
 * category detection, and relevance scoring
 */

// Comprehensive job categories - EVERY type of work supported!
export const JOB_CATEGORIES = {
  // TRADES & SKILLED LABOR
  'Trades & Construction': {
    keywords: ['plumber', 'plumbing', 'pipe fitter', 'electrician', 'electrical', 'wiring', 'carpenter', 'woodwork', 'mason', 'masonry', 'bricklayer', 'roofer', 'roofing', 'hvac', 'heating', 'cooling', 'air conditioning', 'welder', 'welding', 'fabricator', 'painter', 'painting', 'contractor', 'handyman', 'builder', 'construction', 'renovation', 'remodeling', 'repair', 'install', 'installation', 'maintenance', 'tiler', 'flooring', 'drywall', 'concrete', 'scaffolder', 'rigger', 'foreman', 'supervisor', 'surveyor', 'estimator', 'drafter', 'cad', 'demolition', 'excavator', 'heavy equipment', 'crane operator', 'glazier', 'window installer', 'insulation', 'sheet metal', 'ironworker', 'steelworker'],
    icon: '🔧',
    priority: 1
  },
  
  // HEALTHCARE & MEDICAL
  'Healthcare & Medical': {
    keywords: ['doctor', 'physician', 'surgeon', 'specialist', 'gp', 'general practitioner', 'nurse', 'nursing', 'rn', 'lpn', 'cna', 'nurse practitioner', 'dentist', 'dental', 'orthodontist', 'hygienist', 'medical', 'healthcare', 'pharmacy', 'pharmacist', 'technician', 'therapist', 'physical therapy', 'occupational therapy', 'speech therapy', 'counselor', 'psychologist', 'psychiatrist', 'caregiver', 'home health', 'aide', 'clinical', 'hospital', 'health', 'paramedic', 'emt', 'emergency', 'midwife', 'radiologist', 'ultrasound', 'lab technician', 'phlebotomist', 'medical assistant', 'receptionist', 'medical records', 'health information', 'chiropractor', 'optometrist', 'podiatrist', 'dietitian', 'nutritionist', 'respiratory therapist', 'anesthesiologist', 'oncologist', 'cardiologist', 'pediatrician', 'obstetrician', 'veterinarian', 'vet tech', 'animal care'],
    icon: '🏥',
    priority: 1
  },
  
  // HOSPITALITY & TOURISM
  'Hospitality & Tourism': {
    keywords: ['hotel', 'resort', 'motel', 'inn', 'lodge', 'restaurant', 'cafe', 'bistro', 'diner', 'chef', 'head chef', 'sous chef', 'cook', 'line cook', 'prep cook', 'culinary', 'kitchen', 'waiter', 'waitress', 'server', 'bartender', 'barista', 'mixologist', 'sommelier', 'host', 'hostess', 'maitre d', 'tourism', 'tour guide', 'tour operator', 'travel agent', 'hospitality', 'housekeeping', 'housekeeper', 'cleaner', 'concierge', 'front desk', 'receptionist', 'bellhop', 'porter', 'valet', 'event planner', 'catering', 'banquet', 'food service', 'dishwasher', 'busser', 'casino', 'dealer', 'pit boss', 'gaming', 'cruise', 'cabin crew', 'steward', 'spa attendant', 'massage therapist', 'recreation', 'activities coordinator', 'entertainment', 'performer', 'musician', 'dj'],
    icon: '🏨',
    priority: 1
  },
  
  // PROFESSIONAL SERVICES
  'Professional Services': {
    keywords: ['lawyer', 'attorney', 'legal', 'solicitor', 'paralegal', 'accountant', 'cpa', 'bookkeeper', 'auditor', 'tax preparer', 'financial advisor', 'consultant', 'business consultant', 'management consultant', 'advisor', 'analyst', 'business analyst', 'data analyst', 'financial analyst', 'manager', 'general manager', 'operations manager', 'project manager', 'program manager', 'director', 'executive', 'ceo', 'cfo', 'coo', 'president', 'vice president', 'professional', 'administrator', 'coordinator', 'specialist', 'human resources', 'hr', 'recruiter', 'talent acquisition', 'trainer', 'insurance agent', 'broker', 'real estate agent', 'realtor', 'property manager', 'leasing agent', 'mortgage broker', 'loan officer', 'banker', 'teller', 'financial planner', 'investment advisor', 'economist', 'actuary', 'underwriter', 'claims adjuster', 'notary', 'court reporter', 'mediator', 'arbitrator'],
    icon: '💼',
    priority: 1
  },
  
  // TECHNOLOGY & IT
  'Technology & IT': {
    keywords: ['developer', 'software developer', 'web developer', 'mobile developer', 'full stack', 'frontend', 'backend', 'programmer', 'coder', 'software', 'engineer', 'software engineer', 'it', 'information technology', 'computer', 'tech', 'technical', 'designer', 'web designer', 'graphic designer', 'ui designer', 'ux designer', 'product designer', 'web', 'website', 'app', 'application', 'digital', 'systems administrator', 'network administrator', 'database administrator', 'dba', 'devops', 'cloud engineer', 'security', 'cybersecurity', 'information security', 'analyst', 'data scientist', 'data engineer', 'machine learning', 'ai', 'artificial intelligence', 'qa', 'quality assurance', 'tester', 'support', 'technical support', 'help desk', 'it support', 'architect', 'solutions architect', 'scrum master', 'product manager', 'product owner', 'game developer', 'game designer', 'animator', '3d artist', 'video editor', 'multimedia', 'seo specialist', 'digital marketing', 'social media manager', 'content creator', 'blockchain', 'crypto'],
    icon: '💻',
    priority: 1
  },
  
  // EDUCATION & TRAINING
  'Education & Training': {
    keywords: ['teacher', 'educator', 'instructor', 'professor', 'lecturer', 'tutor', 'private tutor', 'education', 'teaching', 'training', 'trainer', 'coach', 'life coach', 'career coach', 'mentor', 'principal', 'headmaster', 'dean', 'administrator', 'counselor', 'guidance counselor', 'school counselor', 'academic advisor', 'librarian', 'teaching assistant', 'teacher aide', 'substitute teacher', 'special education', 'sped', 'early childhood', 'preschool', 'kindergarten', 'elementary', 'secondary', 'high school', 'college', 'university', 'vocational', 'esl', 'english teacher', 'math teacher', 'science teacher', 'music teacher', 'art teacher', 'pe teacher', 'physical education', 'sports coach', 'athletic director', 'curriculum developer', 'instructional designer', 'educational consultant', 'childcare', 'daycare', 'nanny', 'babysitter', 'au pair'],
    icon: '📚',
    priority: 1
  },
  
  // TRANSPORTATION & LOGISTICS
  'Transportation & Logistics': {
    keywords: ['driver', 'truck driver', 'cdl', 'delivery driver', 'courier', 'taxi driver', 'uber', 'lyft', 'chauffeur', 'bus driver', 'school bus', 'transit', 'transport', 'transportation', 'logistics', 'supply chain', 'warehouse', 'forklift operator', 'loader', 'shipping', 'receiving', 'freight', 'cargo', 'dispatcher', 'fleet manager', 'route planner', 'delivery', 'courier service', 'postal worker', 'mail carrier', 'package handler', 'dock worker', 'longshoreman', 'pilot', 'captain', 'first officer', 'flight attendant', 'air traffic controller', 'aircraft mechanic', 'boat captain', 'ferry operator', 'marina', 'port', 'customs', 'import', 'export', 'inventory', 'stock', 'material handler', 'picker', 'packer', 'shipper'],
    icon: '🚗',
    priority: 1
  },
  
  // HOME & PROPERTY SERVICES
  'Home & Property Services': {
    keywords: ['cleaning', 'cleaner', 'housekeeper', 'maid', 'janitor', 'custodian', 'maintenance', 'facility maintenance', 'building maintenance', 'gardener', 'landscaper', 'landscaping', 'lawn care', 'groundskeeper', 'tree trimmer', 'arborist', 'pest control', 'exterminator', 'fumigation', 'security', 'security guard', 'guard', 'watchman', 'patrol', 'bouncer', 'bodyguard', 'private security', 'alarm technician', 'locksmith', 'pool service', 'pool cleaner', 'window cleaner', 'carpet cleaner', 'upholstery', 'junk removal', 'moving', 'mover', 'handyperson', 'home repair', 'appliance repair', 'furniture assembly', 'pressure washing', 'gutter cleaning', 'snow removal', 'property caretaker', 'estate manager', 'superintendent', 'building super'],
    icon: '🏠',
    priority: 1
  },
  
  // BEAUTY, WELLNESS & FITNESS
  'Beauty, Wellness & Fitness': {
    keywords: ['salon', 'barber', 'barber shop', 'hairdresser', 'hair stylist', 'hairstylist', 'beautician', 'cosmetologist', 'makeup artist', 'esthetician', 'spa', 'spa therapist', 'massage', 'massage therapist', 'masseuse', 'stylist', 'nail technician', 'manicurist', 'pedicurist', 'cosmetology', 'beauty', 'skincare', 'facial', 'waxing', 'threading', 'lash technician', 'brow specialist', 'tattoo artist', 'piercer', 'personal trainer', 'fitness instructor', 'gym instructor', 'yoga instructor', 'pilates instructor', 'zumba', 'aerobics', 'crossfit', 'coach', 'fitness coach', 'nutritionist', 'dietician', 'wellness coach', 'health coach', 'physical therapist', 'chiropractor', 'acupuncturist', 'reflexologist', 'holistic', 'naturopath', 'gym manager', 'fitness center', 'recreation', 'lifeguard', 'swim instructor', 'martial arts instructor', 'boxing trainer', 'dance instructor', 'choreographer'],
    icon: '💇',
    priority: 1
  },
  
  // RETAIL & SALES
  'Retail & Sales': {
    keywords: ['sales', 'salesperson', 'sales associate', 'sales rep', 'sales representative', 'account executive', 'business development', 'retail', 'retail associate', 'cashier', 'checkout', 'store', 'store clerk', 'shop assistant', 'shop', 'merchant', 'vendor', 'seller', 'store manager', 'assistant manager', 'shift supervisor', 'key holder', 'merchandiser', 'visual merchandiser', 'buyer', 'purchasing', 'procurement', 'inventory specialist', 'stock clerk', 'stocker', 'product specialist', 'brand ambassador', 'promoter', 'demonstrator', 'customer service', 'service representative', 'call center', 'telemarketer', 'inside sales', 'outside sales', 'field sales', 'territory manager', 'regional manager', 'district manager', 'wholesale', 'distributor', 'retail buyer', 'fashion consultant', 'personal shopper', 'jeweler', 'watch maker', 'optician', 'pharmacist', 'pharmacy technician'],
    icon: '🛍️',
    priority: 1
  },
  
  // MANUFACTURING & PRODUCTION
  'Manufacturing & Production': {
    keywords: ['manufacturing', 'production', 'factory', 'assembly', 'assembler', 'production worker', 'machine operator', 'cnc operator', 'lathe operator', 'mill operator', 'press operator', 'fabricator', 'welder', 'quality control', 'qc inspector', 'quality assurance', 'production supervisor', 'shift supervisor', 'plant manager', 'operations manager', 'maintenance technician', 'industrial mechanic', 'millwright', 'tool and die maker', 'mold maker', 'machinist', 'process engineer', 'manufacturing engineer', 'industrial engineer', 'production planner', 'scheduler', 'material handler', 'forklift', 'warehouse', 'packaging', 'packer', 'palletizer', 'line worker', 'assembly line', 'automation', 'robotics technician', 'electronics technician', 'product development', 'prototype', 'textile worker', 'sewing machine operator', 'cutter', 'food production', 'food processing', 'bottling', 'brewery', 'distillery'],
    icon: '🏭',
    priority: 2
  },
  
  // AGRICULTURE & ENVIRONMENTAL
  'Agriculture & Environmental': {
    keywords: ['agriculture', 'farming', 'farmer', 'farm worker', 'agricultural', 'crop', 'livestock', 'rancher', 'ranch hand', 'farmhand', 'harvester', 'tractor operator', 'agronomist', 'horticulturist', 'greenhouse', 'nursery', 'plant nursery', 'landscaper', 'gardener', 'groundskeeper', 'irrigation', 'fisherman', 'fishing', 'aquaculture', 'fish farm', 'marine biologist', 'environmental', 'environmentalist', 'ecologist', 'conservation', 'conservationist', 'wildlife', 'forest ranger', 'park ranger', 'forester', 'arborist', 'tree surgeon', 'soil scientist', 'geologist', 'environmental engineer', 'sustainability', 'renewable energy', 'solar', 'solar installer', 'wind energy', 'recycling', 'waste management', 'sanitation', 'water treatment', 'wastewater', 'environmental consultant', 'ecology', 'botanist', 'entomologist', 'veterinarian', 'animal trainer', 'zookeeper', 'animal handler'],
    icon: '🌾',
    priority: 2
  },
  
  // ARTS, MEDIA & ENTERTAINMENT
  'Arts, Media & Entertainment': {
    keywords: ['artist', 'painter', 'sculptor', 'illustrator', 'graphic designer', 'designer', 'creative', 'art director', 'photographer', 'videographer', 'cinematographer', 'camera operator', 'film', 'filmmaker', 'director', 'producer', 'editor', 'video editor', 'sound engineer', 'audio engineer', 'music producer', 'musician', 'singer', 'vocalist', 'instrumentalist', 'composer', 'songwriter', 'dj', 'disc jockey', 'entertainer', 'performer', 'actor', 'actress', 'model', 'dancer', 'choreographer', 'theater', 'stage manager', 'production assistant', 'lighting technician', 'sound technician', 'broadcast', 'radio', 'tv', 'television', 'journalist', 'reporter', 'news anchor', 'correspondent', 'writer', 'author', 'copywriter', 'content writer', 'editor', 'proofreader', 'blogger', 'influencer', 'social media', 'content creator', 'youtuber', 'podcaster', 'animator', 'animation', 'voice actor', 'narrator', 'mc', 'master of ceremonies', 'comedian', 'stand-up', 'magician', 'clown', 'face painter', 'event entertainment', 'band', 'orchestra'],
    icon: '🎨',
    priority: 2
  },
  
  // AUTOMOTIVE & MECHANICAL
  'Automotive & Mechanical': {
    keywords: ['mechanic', 'auto mechanic', 'automotive', 'car mechanic', 'technician', 'service technician', 'diesel mechanic', 'heavy equipment mechanic', 'motorcycle mechanic', 'bike mechanic', 'marine mechanic', 'aircraft mechanic', 'automotive engineer', 'auto body', 'body shop', 'collision repair', 'painter', 'auto painter', 'detailer', 'car detailing', 'car wash', 'oil change', 'lube technician', 'tire technician', 'alignment', 'brake specialist', 'transmission specialist', 'electrician', 'auto electrician', 'service advisor', 'service writer', 'parts counter', 'parts manager', 'automotive sales', 'car sales', 'salesperson', 'sales consultant', 'finance manager', 'used car', 'dealership', 'service manager', 'shop foreman', 'smog technician', 'inspection', 'diagnostics', 'mechanic helper', 'apprentice mechanic', 'hvac technician', 'refrigeration', 'industrial mechanic', 'maintenance mechanic', 'millwright', 'machinery', 'equipment operator'],
    icon: '🔩',
    priority: 2
  },
  
  // LEGAL & COMPLIANCE
  'Legal & Compliance': {
    keywords: ['lawyer', 'attorney', 'counsel', 'legal', 'solicitor', 'barrister', 'advocate', 'paralegal', 'legal assistant', 'legal secretary', 'law clerk', 'court clerk', 'judge', 'magistrate', 'legal researcher', 'legal analyst', 'compliance', 'compliance officer', 'regulatory', 'risk management', 'legal counsel', 'corporate lawyer', 'litigation', 'trial lawyer', 'prosecutor', 'public defender', 'criminal lawyer', 'defense attorney', 'civil lawyer', 'family lawyer', 'divorce lawyer', 'estate lawyer', 'probate', 'real estate lawyer', 'immigration lawyer', 'tax lawyer', 'patent lawyer', 'intellectual property', 'contract lawyer', 'mediator', 'arbitrator', 'legal consultant', 'notary', 'notary public', 'court reporter', 'stenographer', 'bailiff', 'process server', 'investigator', 'private investigator', 'detective', 'forensic', 'legal compliance', 'policy analyst'],
    icon: '⚖️',
    priority: 2
  },
  
  // SCIENCE & RESEARCH
  'Science & Research': {
    keywords: ['scientist', 'researcher', 'research', 'laboratory', 'lab', 'lab technician', 'chemist', 'chemistry', 'biologist', 'biology', 'microbiologist', 'biochemist', 'physicist', 'physics', 'engineer', 'chemical engineer', 'biomedical engineer', 'environmental scientist', 'geologist', 'geophysicist', 'meteorologist', 'climatologist', 'oceanographer', 'marine biologist', 'zoologist', 'botanist', 'ecologist', 'geneticist', 'molecular biologist', 'pharmaceutical', 'pharmacologist', 'toxicologist', 'epidemiologist', 'public health', 'clinical research', 'research associate', 'research assistant', 'postdoc', 'postdoctoral', 'phd', 'scientist', 'data scientist', 'statistician', 'analyst', 'research analyst', 'technical writer', 'scientific writer', 'lab manager', 'laboratory manager', 'quality control', 'r&d', 'research and development', 'innovation', 'biotechnology', 'biotech', 'pharmaceutical research', 'materials scientist', 'nanotechnology', 'aerospace engineer'],
    icon: '🔬',
    priority: 2
  },
  
  // FOOD & BEVERAGE PRODUCTION
  'Food & Beverage Production': {
    keywords: ['baker', 'bakery', 'pastry chef', 'pastry cook', 'bread baker', 'cake decorator', 'confectioner', 'chocolatier', 'butcher', 'meat cutter', 'meat processor', 'deli', 'deli clerk', 'food preparation', 'food prep', 'prep cook', 'kitchen helper', 'kitchen assistant', 'food production', 'food manufacturing', 'food processing', 'food safety', 'quality assurance', 'food scientist', 'food technologist', 'brewery', 'brewer', 'brewmaster', 'distillery', 'distiller', 'winemaker', 'vintner', 'sommelier', 'barista', 'coffee roaster', 'coffee shop', 'juice bar', 'smoothie', 'ice cream', 'gelato', 'catering', 'caterer', 'banquet chef', 'dietary aide', 'nutrition', 'food service', 'commissary', 'industrial kitchen', 'restaurant kitchen', 'line cook', 'grill cook', 'fry cook', 'sushi chef', 'pizza maker', 'sandwich artist', 'food truck', 'mobile kitchen', 'personal chef', 'private chef'],
    icon: '🍳',
    priority: 2
  },
  
  // MARITIME & MARINE
  'Maritime & Marine': {
    keywords: ['maritime', 'marine', 'sailor', 'seaman', 'merchant marine', 'captain', 'ship captain', 'boat captain', 'first mate', 'deckhand', 'deck officer', 'engineer', 'marine engineer', 'chief engineer', 'oiler', 'wiper', 'able seaman', 'ordinary seaman', 'bosun', 'boatswain', 'steward', 'cook', 'ship cook', 'purser', 'navigator', 'pilot', 'harbor pilot', 'tugboat', 'tug captain', 'barge', 'ferry', 'ferry operator', 'fishing', 'fisherman', 'commercial fishing', 'fishing vessel', 'charter boat', 'yacht', 'yacht crew', 'crew member', 'marina', 'dock master', 'harbor master', 'port', 'port worker', 'longshoreman', 'stevedore', 'crane operator', 'ship loader', 'marine surveyor', 'naval architect', 'boat builder', 'shipwright', 'marine mechanic', 'marine electrician', 'marine technician', 'diving', 'diver', 'commercial diver', 'salvage diver', 'underwater', 'submarine', 'offshore', 'oil rig', 'platform worker', 'maritime security', 'coast guard'],
    icon: '⚓',
    priority: 2
  },
  
  // AVIATION & AEROSPACE
  'Aviation & Aerospace': {
    keywords: ['aviation', 'pilot', 'airline pilot', 'commercial pilot', 'private pilot', 'captain', 'first officer', 'co-pilot', 'flight engineer', 'flight attendant', 'cabin crew', 'flight crew', 'air hostess', 'steward', 'stewardess', 'ground crew', 'ramp agent', 'baggage handler', 'aircraft mechanic', 'aviation mechanic', 'aircraft technician', 'a&p mechanic', 'avionics', 'avionics technician', 'air traffic controller', 'atc', 'dispatcher', 'flight dispatcher', 'operations', 'airline operations', 'airport', 'airport operations', 'airport security', 'tsa', 'customs', 'immigration', 'gate agent', 'ticket agent', 'reservation agent', 'charter', 'helicopter pilot', 'drone pilot', 'uav', 'aerospace', 'aerospace engineer', 'aeronautical engineer', 'aircraft designer', 'flight test', 'flight instructor', 'cfi', 'aircraft inspector', 'quality control', 'aviation safety', 'flight operations', 'flight planning', 'meteorologist', 'aviation weather', 'hangar', 'line service', 'fueling', 'aircraft cleaner', 'cargo handler', 'freight'],
    icon: '✈️',
    priority: 2
  },
  
  // GOVERNMENT & PUBLIC SERVICE
  'Government & Public Service': {
    keywords: ['government', 'public service', 'civil service', 'federal', 'state', 'county', 'municipal', 'city', 'town', 'clerk', 'administrative', 'administrator', 'coordinator', 'analyst', 'policy', 'policy analyst', 'program manager', 'caseworker', 'social worker', 'social services', 'welfare', 'public assistance', 'benefits', 'eligibility', 'tax', 'tax collector', 'assessor', 'appraiser', 'building inspector', 'code enforcement', 'zoning', 'planning', 'urban planner', 'city planner', 'public works', 'sanitation', 'water', 'utilities', 'meter reader', 'surveyor', 'gis', 'geospatial', 'cartographer', 'records', 'archives', 'archivist', 'historian', 'curator', 'museum', 'gallery', 'library', 'librarian', 'information specialist', 'public information', 'communications', 'press secretary', 'diplomatic', 'diplomat', 'foreign service', 'consular', 'embassy', 'elected official', 'commissioner', 'council member', 'mayor', 'governor', 'senator', 'representative', 'legislative', 'aide', 'staffer', 'paralegal', 'court', 'judicial'],
    icon: '🏛️',
    priority: 2
  },
  
  // EMERGENCY SERVICES
  'Emergency & Public Safety': {
    keywords: ['emergency', 'first responder', 'firefighter', 'fire', 'fire department', 'fire captain', 'fire chief', 'paramedic', 'emt', 'emergency medical', 'ambulance', 'emergency medical technician', 'police', 'police officer', 'cop', 'law enforcement', 'detective', 'investigator', 'sheriff', 'deputy', 'constable', 'marshal', 'security', 'corrections', 'correctional officer', 'prison guard', 'jail', 'probation officer', 'parole officer', 'border patrol', 'customs', 'immigration officer', 'federal agent', 'special agent', 'fbi', 'dea', 'atf', 'secret service', 'marshal', 'dispatcher', '911', 'emergency dispatcher', 'police dispatcher', 'fire dispatcher', 'communications', 'emergency management', 'disaster', 'disaster response', 'hazmat', 'hazardous materials', 'bomb squad', 'swat', 'k9', 'canine handler', 'evidence technician', 'forensic', 'crime scene', 'search and rescue', 'lifeguard', 'ocean safety', 'park ranger', 'game warden', 'wildlife officer', 'safety', 'safety officer', 'safety coordinator', 'osha', 'industrial safety', 'environmental health and safety', 'ehs'],
    icon: '🚨',
    priority: 1
  },
  
  // MILITARY & DEFENSE
  'Military & Defense': {
    keywords: ['military', 'armed forces', 'army', 'navy', 'air force', 'marines', 'coast guard', 'soldier', 'sailor', 'airman', 'marine', 'officer', 'enlisted', 'nco', 'sergeant', 'corporal', 'lieutenant', 'captain', 'major', 'colonel', 'general', 'admiral', 'commander', 'petty officer', 'warrant officer', 'veteran', 'infantry', 'artillery', 'cavalry', 'armor', 'aviation', 'pilot', 'crew chief', 'mechanic', 'engineer', 'combat engineer', 'military police', 'mp', 'intelligence', 'intelligence analyst', 'special forces', 'special operations', 'ranger', 'seal', 'green beret', 'airborne', 'sniper', 'medic', 'combat medic', 'corpsman', 'logistics', 'supply', 'quartermaster', 'transportation', 'communications', 'signal', 'radar', 'sonar', 'electronic warfare', 'cyber', 'cyber warfare', 'information technology', 'instructor', 'drill instructor', 'recruiter', 'military recruiter', 'contractor', 'defense contractor', 'security clearance', 'classified', 'tactical', 'operations', 'strategic', 'defense', 'national security', 'homeland security'],
    icon: '🎖️',
    priority: 2
  },
  
  // ENERGY & UTILITIES
  'Energy & Utilities': {
    keywords: ['energy', 'power', 'electricity', 'electric', 'utility', 'utilities', 'power plant', 'power station', 'generator', 'turbine', 'operator', 'control room', 'nuclear', 'nuclear power', 'coal', 'natural gas', 'oil', 'petroleum', 'refinery', 'drilling', 'rig', 'oil rig', 'driller', 'roughneck', 'roustabout', 'pipeline', 'pipeline operator', 'field technician', 'lineman', 'line worker', 'power line', 'electrician', 'electrical', 'substation', 'transmission', 'distribution', 'meter reader', 'utility worker', 'water', 'water treatment', 'wastewater', 'sewage', 'plant operator', 'water quality', 'environmental', 'gas', 'gas technician', 'hvac', 'heating', 'cooling', 'refrigeration', 'boiler', 'boiler operator', 'stationary engineer', 'maintenance', 'renewable', 'renewable energy', 'solar', 'solar installer', 'photovoltaic', 'wind', 'wind turbine', 'wind technician', 'geothermal', 'hydroelectric', 'dam', 'sustainability', 'energy efficiency', 'energy auditor', 'smart grid', 'energy analyst', 'energy engineer', 'petroleum engineer'],
    icon: '⚡',
    priority: 2
  },
  
  // GENERAL LABOR & MISCELLANEOUS
  'General Labor & Other': {
    keywords: ['general labor', 'laborer', 'worker', 'helper', 'assistant', 'apprentice', 'trainee', 'intern', 'internship', 'temp', 'temporary', 'seasonal', 'part-time', 'full-time', 'contract', 'freelance', 'independent contractor', 'consultant', 'gig', 'odd jobs', 'handyman', 'jack of all trades', 'entry level', 'no experience', 'unskilled', 'semi-skilled', 'skilled', 'experienced', 'senior', 'lead', 'supervisor', 'foreman', 'crew leader', 'team leader', 'shift leader', 'coordinator', 'specialist', 'technician', 'operator', 'attendant', 'associate', 'representative', 'agent', 'clerk', 'secretary', 'receptionist', 'office', 'administrative', 'data entry', 'filing', 'typing', 'clerical', 'support', 'customer service', 'call center', 'telecommute', 'remote', 'work from home', 'virtual', 'online', 'startup', 'small business', 'entrepreneur', 'business owner', 'self-employed', 'work', 'job', 'employment', 'career', 'position', 'opening', 'vacancy', 'hiring', 'now hiring', 'immediately', 'urgent', 'needed', 'wanted', 'seeking', 'looking for', 'opportunity', 'apply', 'application'],
    icon: '👷',
    priority: 3
  }
};

// Common search variations and corrections
export const SEARCH_SYNONYMS: Record<string, string[]> = {
  'plumber': ['plumbing', 'pipe fitter', 'drain cleaner', 'pipefitter'],
  'electrician': ['electrical', 'electric', 'wiring', 'electronics'],
  'carpenter': ['woodwork', 'woodworker', 'cabinet maker', 'joiner'],
  'chef': ['cook', 'culinary', 'kitchen', 'food prep'],
  'developer': ['programmer', 'coder', 'software engineer'],
  'driver': ['chauffeur', 'operator'],
  'teacher': ['educator', 'instructor'],
  'cleaner': ['cleaning', 'janitor', 'housekeeper', 'maid'],
  'mechanic': ['auto repair', 'automotive', 'technician'],
  'lawyer': ['attorney', 'legal', 'solicitor'],
};

// Location data for Bahamas
export const BAHAMAS_LOCATIONS = [
  'Nassau',
  'Freeport',
  'Grand Bahama',
  'Paradise Island',
  'Abaco',
  'Eleuthera',
  'Exuma',
  'Andros',
  'Bimini',
  'Long Island',
  'Cat Island',
  'San Salvador',
  'Harbour Island'
];

/**
 * Calculate similarity between two strings using Levenshtein distance
 */
function calculateSimilarity(str1: string, str2: string): number {
  const s1 = str1.toLowerCase();
  const s2 = str2.toLowerCase();
  
  // Exact match
  if (s1 === s2) return 1.0;
  
  // Contains match
  if (s1.includes(s2) || s2.includes(s1)) return 0.8;
  
  // Levenshtein distance
  const matrix: number[][] = [];
  
  for (let i = 0; i <= s2.length; i++) {
    matrix[i] = [i];
  }
  
  for (let j = 0; j <= s1.length; j++) {
    matrix[0][j] = j;
  }
  
  for (let i = 1; i <= s2.length; i++) {
    for (let j = 1; j <= s1.length; j++) {
      if (s2.charAt(i - 1) === s1.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j] + 1
        );
      }
    }
  }
  
  const maxLength = Math.max(s1.length, s2.length);
  const similarity = 1 - matrix[s2.length][s1.length] / maxLength;
  
  return similarity;
}

/**
 * Detect categories from search query
 */
export function detectCategories(query: string): Array<{ category: string; confidence: number; icon: string }> {
  const lowercaseQuery = query.toLowerCase();
  const detectedCategories: Array<{ category: string; confidence: number; icon: string }> = [];
  
  Object.entries(JOB_CATEGORIES).forEach(([category, data]) => {
    let maxConfidence = 0;
    
    data.keywords.forEach(keyword => {
      const similarity = calculateSimilarity(lowercaseQuery, keyword);
      
      // Check if query contains the keyword
      if (lowercaseQuery.includes(keyword) || keyword.includes(lowercaseQuery)) {
        maxConfidence = Math.max(maxConfidence, 0.9);
      } else if (similarity > 0.7) {
        maxConfidence = Math.max(maxConfidence, similarity);
      }
      
      // Check synonyms
      if (SEARCH_SYNONYMS[keyword]) {
        SEARCH_SYNONYMS[keyword].forEach(syn => {
          if (lowercaseQuery.includes(syn) || syn.includes(lowercaseQuery)) {
            maxConfidence = Math.max(maxConfidence, 0.85);
          }
        });
      }
    });
    
    if (maxConfidence > 0.6) {
      detectedCategories.push({
        category,
        confidence: maxConfidence,
        icon: data.icon
      });
    }
  });
  
  // Sort by confidence
  return detectedCategories.sort((a, b) => b.confidence - a.confidence);
}

/**
 * Generate search suggestions based on partial input
 */
export function generateSearchSuggestions(query: string, limit: number = 5): string[] {
  if (!query || query.length < 2) return [];
  
  const lowercaseQuery = query.toLowerCase();
  const suggestions: Array<{ text: string; score: number }> = [];
  
  // Check all keywords from categories
  Object.values(JOB_CATEGORIES).forEach(category => {
    category.keywords.forEach(keyword => {
      if (keyword.startsWith(lowercaseQuery)) {
        suggestions.push({ text: keyword, score: 1.0 });
      } else if (keyword.includes(lowercaseQuery)) {
        suggestions.push({ text: keyword, score: 0.8 });
      } else {
        const similarity = calculateSimilarity(lowercaseQuery, keyword);
        if (similarity > 0.7) {
          suggestions.push({ text: keyword, score: similarity });
        }
      }
    });
  });
  
  // Add location suggestions
  BAHAMAS_LOCATIONS.forEach(location => {
    if (location.toLowerCase().startsWith(lowercaseQuery)) {
      suggestions.push({ text: `Jobs in ${location}`, score: 0.9 });
    }
  });
  
  // Sort by score and remove duplicates
  const uniqueSuggestions = Array.from(
    new Set(suggestions.map(s => s.text))
  ).map(text => ({
    text,
    score: Math.max(...suggestions.filter(s => s.text === text).map(s => s.score))
  }));
  
  return uniqueSuggestions
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map(s => s.text);
}

/**
 * Calculate relevance score for a job posting
 */
export interface JobSearchResult {
  id: number;
  title: string;
  description: string;
  category: string;
  location: string;
  company?: string;
  skills?: string[];
  relevanceScore: number;
  matchedFields: string[];
}

export function calculateJobRelevance(
  job: any,
  searchQuery: string
): { score: number; matchedFields: string[] } {
  if (!searchQuery) return { score: 1, matchedFields: [] };
  
  const query = searchQuery.toLowerCase();
  const matchedFields: string[] = [];
  let score = 0;
  
  // Title match (highest weight)
  if (job.title) {
    const titleSimilarity = calculateSimilarity(query, job.title);
    if (titleSimilarity > 0.5) {
      score += titleSimilarity * 40;
      matchedFields.push('title');
    }
  }
  
  // Category match
  if (job.category) {
    const categorySimilarity = calculateSimilarity(query, job.category);
    if (categorySimilarity > 0.5) {
      score += categorySimilarity * 25;
      matchedFields.push('category');
    }
  }
  
  // Description match
  if (job.description) {
    if (job.description.toLowerCase().includes(query)) {
      score += 15;
      matchedFields.push('description');
    }
  }
  
  // Company match
  if (job.company) {
    const companySimilarity = calculateSimilarity(query, job.company);
    if (companySimilarity > 0.5) {
      score += companySimilarity * 10;
      matchedFields.push('company');
    }
  }
  
  // Skills match
  if (job.skills && Array.isArray(job.skills)) {
    job.skills.forEach((skill: string) => {
      if (calculateSimilarity(query, skill) > 0.7) {
        score += 5;
        if (!matchedFields.includes('skills')) {
          matchedFields.push('skills');
        }
      }
    });
  }
  
  // Location boost (if matches)
  if (job.location) {
    const locationSimilarity = calculateSimilarity(query, job.location);
    if (locationSimilarity > 0.7) {
      score += 10;
      matchedFields.push('location');
    }
  }
  
  // Normalize score to 0-100
  return { score: Math.min(100, score), matchedFields };
}

/**
 * Main search function with intelligent filtering
 */
export function smartSearch(
  jobs: any[],
  searchQuery: string,
  filters?: {
    category?: string;
    location?: string;
    minRelevance?: number;
  }
): JobSearchResult[] {
  if (!searchQuery && !filters?.category && !filters?.location) {
    return jobs.map(job => ({
      ...job,
      relevanceScore: 100,
      matchedFields: []
    }));
  }
  
  const results: JobSearchResult[] = [];
  const minRelevance = filters?.minRelevance || 30;
  
  jobs.forEach(job => {
    const { score, matchedFields } = calculateJobRelevance(job, searchQuery);
    
    // Apply category filter
    if (filters?.category && job.category !== filters.category) {
      return;
    }
    
    // Apply location filter
    if (filters?.location && !job.location.toLowerCase().includes(filters.location.toLowerCase())) {
      return;
    }
    
    // Only include results above minimum relevance threshold
    if (score >= minRelevance || matchedFields.length > 0) {
      results.push({
        ...job,
        relevanceScore: score,
        matchedFields
      });
    }
  });
  
  // Sort by relevance score
  return results.sort((a, b) => b.relevanceScore - a.relevanceScore);
}

/**
 * Popular searches - covering ALL major work types
 */
export const POPULAR_SEARCHES = [
  // Trades & Construction
  { text: 'Plumber', icon: '🔧', category: 'Trades & Construction' },
  { text: 'Electrician', icon: '⚡', category: 'Trades & Construction' },
  { text: 'Carpenter', icon: '🪚', category: 'Trades & Construction' },
  { text: 'Mason', icon: '🧱', category: 'Trades & Construction' },
  { text: 'Welder', icon: '🔥', category: 'Trades & Construction' },
  { text: 'HVAC Technician', icon: '❄️', category: 'Trades & Construction' },
  { text: 'Painter', icon: '🎨', category: 'Trades & Construction' },
  { text: 'Roofer', icon: '🏠', category: 'Trades & Construction' },
  
  // Healthcare & Medical
  { text: 'Nurse', icon: '👨‍⚕️', category: 'Healthcare & Medical' },
  { text: 'Doctor', icon: '🩺', category: 'Healthcare & Medical' },
  { text: 'Dentist', icon: '🦷', category: 'Healthcare & Medical' },
  { text: 'Caregiver', icon: '❤️', category: 'Healthcare & Medical' },
  { text: 'Medical Assistant', icon: '💊', category: 'Healthcare & Medical' },
  { text: 'Pharmacist', icon: '💉', category: 'Healthcare & Medical' },
  { text: 'Physical Therapist', icon: '🏃', category: 'Healthcare & Medical' },
  { text: 'Paramedic', icon: '🚑', category: 'Healthcare & Medical' },
  
  // Hospitality & Tourism
  { text: 'Chef', icon: '👨‍🍳', category: 'Hospitality & Tourism' },
  { text: 'Hotel Jobs', icon: '🏨', category: 'Hospitality & Tourism' },
  { text: 'Waiter', icon: '🍽️', category: 'Hospitality & Tourism' },
  { text: 'Bartender', icon: '🍹', category: 'Hospitality & Tourism' },
  { text: 'Tour Guide', icon: '🗺️', category: 'Hospitality & Tourism' },
  { text: 'Housekeeper', icon: '🧹', category: 'Hospitality & Tourism' },
  { text: 'Concierge', icon: '🛎️', category: 'Hospitality & Tourism' },
  { text: 'Resort Staff', icon: '🏖️', category: 'Hospitality & Tourism' },
  
  // Professional Services
  { text: 'Accountant', icon: '💼', category: 'Professional Services' },
  { text: 'Lawyer', icon: '⚖️', category: 'Professional Services' },
  { text: 'Real Estate Agent', icon: '🏘️', category: 'Professional Services' },
  { text: 'Manager', icon: '📊', category: 'Professional Services' },
  { text: 'Consultant', icon: '💡', category: 'Professional Services' },
  { text: 'HR Specialist', icon: '👥', category: 'Professional Services' },
  { text: 'Financial Advisor', icon: '💰', category: 'Professional Services' },
  { text: 'Project Manager', icon: '📋', category: 'Professional Services' },
  
  // Technology & IT
  { text: 'Developer', icon: '💻', category: 'Technology & IT' },
  { text: 'Web Designer', icon: '🖥️', category: 'Technology & IT' },
  { text: 'IT Support', icon: '🔧', category: 'Technology & IT' },
  { text: 'Network Administrator', icon: '🌐', category: 'Technology & IT' },
  { text: 'Software Engineer', icon: '⚙️', category: 'Technology & IT' },
  { text: 'Data Analyst', icon: '📈', category: 'Technology & IT' },
  { text: 'Graphic Designer', icon: '🎨', category: 'Technology & IT' },
  { text: 'Cybersecurity', icon: '🔐', category: 'Technology & IT' },
  
  // Education & Training
  { text: 'Teacher', icon: '👨‍🏫', category: 'Education & Training' },
  { text: 'Tutor', icon: '📚', category: 'Education & Training' },
  { text: 'Coach', icon: '🏅', category: 'Education & Training' },
  { text: 'Instructor', icon: '👩‍🏫', category: 'Education & Training' },
  { text: 'Daycare Worker', icon: '👶', category: 'Education & Training' },
  { text: 'Professor', icon: '🎓', category: 'Education & Training' },
  { text: 'School Administrator', icon: '📝', category: 'Education & Training' },
  { text: 'Special Education', icon: '💙', category: 'Education & Training' },
  
  // Transportation & Logistics
  { text: 'Driver', icon: '🚗', category: 'Transportation & Logistics' },
  { text: 'Delivery Driver', icon: '📦', category: 'Transportation & Logistics' },
  { text: 'Truck Driver', icon: '🚚', category: 'Transportation & Logistics' },
  { text: 'Warehouse Worker', icon: '📦', category: 'Transportation & Logistics' },
  { text: 'Forklift Operator', icon: '🏗️', category: 'Transportation & Logistics' },
  { text: 'Courier', icon: '🏃', category: 'Transportation & Logistics' },
  { text: 'Logistics Coordinator', icon: '📋', category: 'Transportation & Logistics' },
  { text: 'Dispatcher', icon: '📞', category: 'Transportation & Logistics' },
  
  // Home & Property Services
  { text: 'Cleaner', icon: '🧹', category: 'Home & Property Services' },
  { text: 'Gardener', icon: '🌿', category: 'Home & Property Services' },
  { text: 'Security Guard', icon: '👮', category: 'Home & Property Services' },
  { text: 'Landscaper', icon: '🌳', category: 'Home & Property Services' },
  { text: 'Pest Control', icon: '🐜', category: 'Home & Property Services' },
  { text: 'Property Manager', icon: '🏢', category: 'Home & Property Services' },
  { text: 'Maintenance Worker', icon: '🔧', category: 'Home & Property Services' },
  { text: 'Janitor', icon: '🧽', category: 'Home & Property Services' },
  
  // Beauty, Wellness & Fitness
  { text: 'Barber', icon: '💈', category: 'Beauty, Wellness & Fitness' },
  { text: 'Hair Stylist', icon: '💇', category: 'Beauty, Wellness & Fitness' },
  { text: 'Massage Therapist', icon: '💆', category: 'Beauty, Wellness & Fitness' },
  { text: 'Personal Trainer', icon: '💪', category: 'Beauty, Wellness & Fitness' },
  { text: 'Esthetician', icon: '✨', category: 'Beauty, Wellness & Fitness' },
  { text: 'Nail Technician', icon: '💅', category: 'Beauty, Wellness & Fitness' },
  { text: 'Yoga Instructor', icon: '🧘', category: 'Beauty, Wellness & Fitness' },
  { text: 'Spa Therapist', icon: '🌸', category: 'Beauty, Wellness & Fitness' },
  
  // Retail & Sales
  { text: 'Sales Associate', icon: '🛍️', category: 'Retail & Sales' },
  { text: 'Cashier', icon: '💵', category: 'Retail & Sales' },
  { text: 'Store Manager', icon: '🏪', category: 'Retail & Sales' },
  { text: 'Sales Representative', icon: '📊', category: 'Retail & Sales' },
  { text: 'Merchandiser', icon: '📦', category: 'Retail & Sales' },
  { text: 'Customer Service', icon: '🤝', category: 'Retail & Sales' },
  { text: 'Retail Buyer', icon: '🛒', category: 'Retail & Sales' },
  { text: 'Stock Clerk', icon: '📋', category: 'Retail & Sales' },
  
  // Manufacturing & Production
  { text: 'Machine Operator', icon: '🏭', category: 'Manufacturing & Production' },
  { text: 'Production Worker', icon: '⚙️', category: 'Manufacturing & Production' },
  { text: 'Quality Control', icon: '✅', category: 'Manufacturing & Production' },
  { text: 'Assembly Worker', icon: '🔩', category: 'Manufacturing & Production' },
  { text: 'Factory Worker', icon: '🏭', category: 'Manufacturing & Production' },
  { text: 'Forklift Driver', icon: '🚜', category: 'Manufacturing & Production' },
  { text: 'Packager', icon: '📦', category: 'Manufacturing & Production' },
  { text: 'Industrial Mechanic', icon: '🔧', category: 'Manufacturing & Production' },
  
  // Agriculture & Environmental
  { text: 'Farm Worker', icon: '🌾', category: 'Agriculture & Environmental' },
  { text: 'Landscaper', icon: '🌳', category: 'Agriculture & Environmental' },
  { text: 'Fisherman', icon: '🎣', category: 'Agriculture & Environmental' },
  { text: 'Environmental Specialist', icon: '♻️', category: 'Agriculture & Environmental' },
  { text: 'Greenhouse Worker', icon: '🌱', category: 'Agriculture & Environmental' },
  { text: 'Park Ranger', icon: '🏞️', category: 'Agriculture & Environmental' },
  { text: 'Arborist', icon: '🌲', category: 'Agriculture & Environmental' },
  { text: 'Conservation Worker', icon: '🦋', category: 'Agriculture & Environmental' },
  
  // Arts, Media & Entertainment
  { text: 'Photographer', icon: '📸', category: 'Arts, Media & Entertainment' },
  { text: 'Musician', icon: '🎵', category: 'Arts, Media & Entertainment' },
  { text: 'DJ', icon: '🎧', category: 'Arts, Media & Entertainment' },
  { text: 'Video Editor', icon: '🎬', category: 'Arts, Media & Entertainment' },
  { text: 'Writer', icon: '✍️', category: 'Arts, Media & Entertainment' },
  { text: 'Artist', icon: '🎨', category: 'Arts, Media & Entertainment' },
  { text: 'Event Planner', icon: '🎉', category: 'Arts, Media & Entertainment' },
  { text: 'Social Media Manager', icon: '📱', category: 'Arts, Media & Entertainment' },
  
  // Automotive & Mechanical
  { text: 'Mechanic', icon: '🔩', category: 'Automotive & Mechanical' },
  { text: 'Auto Technician', icon: '🚗', category: 'Automotive & Mechanical' },
  { text: 'Diesel Mechanic', icon: '🚛', category: 'Automotive & Mechanical' },
  { text: 'Body Shop', icon: '🏗️', category: 'Automotive & Mechanical' },
  { text: 'Car Detailer', icon: '🧽', category: 'Automotive & Mechanical' },
  { text: 'Tire Technician', icon: '⚙️', category: 'Automotive & Mechanical' },
  { text: 'Service Advisor', icon: '📋', category: 'Automotive & Mechanical' },
  { text: 'Parts Counter', icon: '🔧', category: 'Automotive & Mechanical' },
  
  // Food & Beverage Production
  { text: 'Baker', icon: '🍞', category: 'Food & Beverage Production' },
  { text: 'Butcher', icon: '🥩', category: 'Food & Beverage Production' },
  { text: 'Food Production', icon: '🍳', category: 'Food & Beverage Production' },
  { text: 'Brewery Worker', icon: '🍺', category: 'Food & Beverage Production' },
  { text: 'Barista', icon: '☕', category: 'Food & Beverage Production' },
  { text: 'Pastry Chef', icon: '🧁', category: 'Food & Beverage Production' },
  { text: 'Food Prep', icon: '🔪', category: 'Food & Beverage Production' },
  { text: 'Line Cook', icon: '👨‍🍳', category: 'Food & Beverage Production' },
  
  // Emergency & Public Safety
  { text: 'Firefighter', icon: '🚒', category: 'Emergency & Public Safety' },
  { text: 'Police Officer', icon: '👮', category: 'Emergency & Public Safety' },
  { text: 'Paramedic', icon: '🚑', category: 'Emergency & Public Safety' },
  { text: 'Security Guard', icon: '🛡️', category: 'Emergency & Public Safety' },
  { text: 'EMT', icon: '🏥', category: 'Emergency & Public Safety' },
  { text: 'Dispatcher', icon: '☎️', category: 'Emergency & Public Safety' },
  { text: 'Correctional Officer', icon: '🔒', category: 'Emergency & Public Safety' },
  { text: 'Lifeguard', icon: '🏊', category: 'Emergency & Public Safety' },
  
  // Maritime & Marine
  { text: 'Boat Captain', icon: '⚓', category: 'Maritime & Marine' },
  { text: 'Deckhand', icon: '🚢', category: 'Maritime & Marine' },
  { text: 'Fisherman', icon: '🎣', category: 'Maritime & Marine' },
  { text: 'Marina Worker', icon: '⛵', category: 'Maritime & Marine' },
  { text: 'Marine Mechanic', icon: '🔧', category: 'Maritime & Marine' },
  { text: 'Ferry Operator', icon: '🛥️', category: 'Maritime & Marine' },
  { text: 'Charter Captain', icon: '🚤', category: 'Maritime & Marine' },
  { text: 'Dock Worker', icon: '🏗️', category: 'Maritime & Marine' },
  
  // General & Other
  { text: 'Administrative Assistant', icon: '📋', category: 'General Labor & Other' },
  { text: 'Receptionist', icon: '📞', category: 'General Labor & Other' },
  { text: 'Data Entry', icon: '⌨️', category: 'General Labor & Other' },
  { text: 'General Labor', icon: '👷', category: 'General Labor & Other' },
  { text: 'Office Manager', icon: '🏢', category: 'General Labor & Other' },
  { text: 'Remote Jobs', icon: '🏠', category: 'General Labor & Other' },
  { text: 'Part Time', icon: '⏰', category: 'General Labor & Other' },
  { text: 'Seasonal Work', icon: '🌴', category: 'General Labor & Other' },
];

/**
 * Extract skills from job description using NLP-like patterns
 */
export function extractSkills(text: string): string[] {
  const skillPatterns = [
    /(?:experience with|proficient in|knowledge of|skilled in)\s+([a-zA-Z\s,]+)/gi,
    /(?:must have|should have|require[sd]?)\s+([a-zA-Z\s,]+)/gi,
  ];
  
  const skills = new Set<string>();
  
  skillPatterns.forEach(pattern => {
    const matches = text.matchAll(pattern);
    for (const match of matches) {
      const skillText = match[1];
      skillText.split(',').forEach(skill => {
        const trimmed = skill.trim();
        if (trimmed.length > 2 && trimmed.length < 30) {
          skills.add(trimmed);
        }
      });
    }
  });
  
  return Array.from(skills);
}
