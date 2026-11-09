// Edge cases: an octal escape and a second hex escape followed by more characters.
namespace kv::rule_5_13_2::bad_edge {

const char* octal() { return "\101B"; }  // seeded
const char* hex() { return "\x7Fq"; }  // seeded

}  // namespace kv::rule_5_13_2::bad_edge
