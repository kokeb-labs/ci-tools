// Edge cases: unknown escapes in a character literal and in a second string.
namespace kv::rule_5_13_1::bad_edge {

char letter() { return '\k'; }  // seeded
const char* label() { return "tab\cend"; }  // seeded

}  // namespace kv::rule_5_13_1::bad_edge
