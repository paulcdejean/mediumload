#!/bin/bash
curl -c /tmp/cookie-jar -d 'mysql%5Bdatabase%5D=50000_drupal&form_build_id=form-8fc9f58dafded5ed67ad33471afd794f57f5d2d43d6d2dec5617e59142ec02b2&mysql%5Bdb_prefix%5D=&form_id=install_settings_form&mysql%5Bport%5D=3306&mysql%5Bhost%5D=appsdb.appcenter123.com&mysql%5Bpassword%5D=gyzaojmwezpnazb&mysql%5Busername%5D=50000&op=Save+and+continue' 'http://civicrm.appcenter123.com/test.appcenter123.com/install.php?profile=minimal&locale=en'