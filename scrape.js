let company_name = 'Smartcar';

company_name = company_name
  .split(' ')
  .join('-')
  .toLowerCase();
console.log(company_name);
var request = require('request');

var options = {
  method: 'GET',
  url:
    'https://www.crunchbase.com/v4/data/entities/organizations/' +
    company_name +
    '?field_ids=%5B%22identifier%22,%22layout_id%22,%22facet_ids%22,%22title%22,%22short_description%22,%22is_unlocked%22%5D&layout_mode=view',
  headers: {
    'cache-control': 'no-cache',
    Connection: 'keep-alive',
    cookie:
      '__cfduid=d49a6d0ab174096bf60ab4584ba9968ad1562790556; cid=rBsAsF0mSpzCugAmV5hDAg==; _pxhd=38a60421661568aff5ac8c606b465cfc50bc2a58ffde727e5f758597799c2977:630c74f1-a351-11e9-8735-a7757449f716',
    Host: 'www.crunchbase.com',
    'Cache-Control': 'no-cache',
    Accept: '*/*',
    'User-Agent': 'PostmanRuntime/7.15.0',
  },
};

request(options, function(error, response, body) {
  if (error) throw new Error(error);

  const res = JSON.parse(body);

  const companyBasics = Object.values(res.cards.overview_company_fields).join(
    ','
  );

  const location = res.cards.overview_fields.location_group_identifiers | {};
  const founded_on = res.cards.overview_fields.founded_on.value || '';
  const founders = res.cards.overview_fields.founder_identifiers || {};
  for (founder in Object.keys(founders)) {
    founders[founder] = founders[founder].value;
  }

  for (loc in Object.keys(location)) {
    location[loc] = location[loc].value;
  }

  const social_media = res.cards.overview_fields2;
  for (item in social_media) {
    if (typeof social_media[item] != 'string') {
      social_media[item] = social_media[item]['value'];
    }
  }

  const investors = res.cards.investors_list;
  for (investor in Object.keys(investors)) {
    investors[investor] = investors[investor].investor_identifier.value;
  }

  let employeeCount = res.cards.overview_fields.num_employees_enum
    .replace('c-', '')
    .replace('_', '-');

  employeeCount = employeeCount.replace('c-', '').replace('_', ' to ');

  const result = {
    company: companyBasics,
    founders: founders == {} ? 'unknown' : founders,
    founded_on,
    location: location ? location.join(',') : 'unknown',
    online_presence: social_media,
    investors,
  };
  console.log(result);
});
