// Seeded violation: a named signed bit-field of width one (it can only hold 0 and -1).
namespace kv::rule_12_2_3::bad {

struct Bits {
  signed int enabled : 1;  // seeded
};

bool on(const Bits& b) { return b.enabled != 0; }

}  // namespace kv::rule_12_2_3::bad
