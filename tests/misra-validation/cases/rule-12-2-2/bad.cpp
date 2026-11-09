// Seeded violation: bit-fields of wchar_t and plain char, which are not signed or unsigned integer types.
namespace kv::rule_12_2_2::bad {

struct Packed {
  wchar_t wide : 4;  // seeded
  char tag : 3;      // seeded
};

bool tagged(const Packed& p) { return (p.tag != 0) || (p.wide != 0); }

}  // namespace kv::rule_12_2_2::bad
