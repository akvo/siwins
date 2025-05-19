# Set to True to enable deletion of outlier data after the seeding process.
# File: seeder/delete_outlier_data.py
ENABLE_DELETE_OUTLIER_DATA = False

# Set to True to enable filtering of incoming data based on school ranking,
# in cases where multiple entries share the same school code.
ENABLE_RANKING_CHECK_FOR_SAME_SCHOOL_CODE = False

# Set to True to enable filtering of incoming data based on same school code
ENABLE_CHECK_FOR_SAME_SCHOOL_CODE = True

# Set to False to enable get school information from question answer
# instead of creating it manually
ENABLE_MANUAL_SCHOOL_INFOMATION = True
