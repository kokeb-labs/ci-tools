// Seeded violation: an unknown escape.

namespace kv::rule_5_13_1_raw_string::bad {

const char* path() { return "dir\qfile"; }

}  // namespace kv::rule_5_13_1_raw_string::bad
