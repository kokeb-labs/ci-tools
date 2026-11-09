// Seeded violation: an explicit specialisation of a member function template.
#include <cstdint>

namespace kv::rule_17_8_1::bad_member {

struct Codec {
  template <typename T>
  static T decode(T v) {
    return v;
  }
};

template <>
std::uint8_t Codec::decode<std::uint8_t>(std::uint8_t v) {  // seeded
  return static_cast<std::uint8_t>(v & 0x7FU);
}

}  // namespace kv::rule_17_8_1::bad_member
