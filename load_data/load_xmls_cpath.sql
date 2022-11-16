INSERT INTO users
  SELECT (xpath('//row/@Id', x))[1]::text::int AS id,
         (xpath('//row/@ExcerptPostId', x))[1]::text::int AS account_id,
         (xpath('//row/@ExcerptPostId', x))[1]::text::int AS reputation,
         (xpath('//row/@ExcerptPostId', x))[1]::text::int AS views,
         (xpath('//row/@ExcerptPostId', x))[1]::text::int AS down_votes,
         (xpath('//row/@ExcerptPostId', x))[1]::text::int AS up_votes,
         (xpath('//row/@ExcerptPostId', x))[1]::text AS display_name,
         (xpath('//row/@ExcerptPostId', x))[1]::text AS location,
         (xpath('//row/@ExcerptPostId', x))[1]::text AS profile_image_url,
         (xpath('//row/@ExcerptPostId', x))[1]::text AS website_url,
         (xpath('//row/@ExcerptPostId', x))[1]::text AS about_me,
         (xpath('//row/@ExcerptPostId', x))[1]::text::timestamp AS creation_date,
         (xpath('//row/@ExcerptPostId', x))[1]::text::timestamp AS last_access_date
  FROM unnest(xpath('//row', pg_read_file('Users.xml')::xml)) x;
  
  