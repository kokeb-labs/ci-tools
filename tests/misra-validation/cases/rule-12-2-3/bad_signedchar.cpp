// Seeded violation (signedchar): a named one-bit bit-field of signed char.

namespace kv::rule_12_2_3::bad_signedchar {

struct Bits {
  signed char flag : 1;
};

bool on(const Bits& b) { return b.flag != 0; }

}  // namespace kv::rule_12_2_3::bad_signedchar
