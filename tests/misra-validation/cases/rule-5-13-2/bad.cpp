// Seeded violation: a hexadecimal escape followed by more characters in the same literal.
namespace kv::rule_5_13_2::bad {

const char* tag() { return "\x41Z"; }

}  // namespace kv::rule_5_13_2::bad
