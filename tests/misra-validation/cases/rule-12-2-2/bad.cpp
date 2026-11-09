// Seeded violation: bit-fields of plain int and plain char, whose signedness is implementation-defined.
namespace kv::rule_12_2_2::bad {

struct Packed {
  int level : 4;
  char tag : 3;
};

int level_of(const Packed& p) { return p.level; }

}  // namespace kv::rule_12_2_2::bad
