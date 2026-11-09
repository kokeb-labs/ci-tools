// Seeded violation: a backslash that starts no valid escape sequence.
namespace kv::rule_5_13_1::bad {

const char* path() { return "dir\qfile"; }  // seeded

}  // namespace kv::rule_5_13_1::bad
