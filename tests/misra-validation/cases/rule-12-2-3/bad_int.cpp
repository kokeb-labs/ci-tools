// Seeded violation (int): a named one-bit bit-field of plain int, which is signed.
namespace kv::rule_12_2_3::bad_int {

struct Bits {
  int ready : 1;  // seeded
};

bool on(const Bits& b) { return b.ready != 0; }

}  // namespace kv::rule_12_2_3::bad_int
