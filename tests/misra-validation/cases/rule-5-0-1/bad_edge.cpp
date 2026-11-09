// Edge cases: more trigraph-like sequences in literals.
namespace kv::rule_5_0_1::bad_edge {

const char* hash() { return "??="; }
const char* brackets() { return "a??(b??)c"; }
char slash() { return "??/"[0]; }

}  // namespace kv::rule_5_0_1::bad_edge
