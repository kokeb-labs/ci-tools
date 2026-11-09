// Edge cases: more trigraph-like sequences in literals.
namespace kv::rule_5_0_1::bad_edge {

const char* hash() { return "??="; }  // seeded
const char* brackets() { return "a??(b??)c"; }  // seeded
char slash() { return "??/"[0]; }  // seeded

}  // namespace kv::rule_5_0_1::bad_edge
