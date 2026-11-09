// Seeded violation (char): a bit-field of plain char only.

namespace kv::rule_12_2_2::bad_char {

struct Tag {
  char kind : 3;  // seeded
};

bool tagged(const Tag& t) { return t.kind != 0; }

}  // namespace kv::rule_12_2_2::bad_char
