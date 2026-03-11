UNWIND [
  {name:'Uganda', iso3:'UGA', identifier:'cc-uga', createdAt:datetime(), lastUpdated:datetime(), verificationStatus:'AUTO_ACCEPTED', hasTag: ['africa']},
  {name:'Ethiopia', iso3:'ETH', identifier:'cc-eth', createdAt:datetime(), lastUpdated:datetime(), verificationStatus:'AUTO_ACCEPTED', hasTag: ['africa']}
] AS row
CREATE (:Country:GeographicEntity:Entity {
  name: row.name, iso3: row.iso3, identifier: row.identifier, createdAt: row.createdAt, lastUpdated: row.lastUpdated, verificationStatus: row.verificationStatus, hasTag: row.hasTag
});
