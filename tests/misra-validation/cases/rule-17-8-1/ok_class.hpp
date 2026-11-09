// Near miss: a class template may be specialised.
#ifndef KV_RULE_17_8_1_OK_CLASS_HPP
#define KV_RULE_17_8_1_OK_CLASS_HPP

#include <cstdint>

namespace kv::rule_17_8_1::ok_class {

template <typename T>
struct Width {
  static constexpr std::uint8_t kBits = 32U;
};

template <>
struct Width<std::uint8_t> {
  static constexpr std::uint8_t kBits = 8U;
};

}  // namespace kv::rule_17_8_1::ok_class

#endif  // KV_RULE_17_8_1_OK_CLASS_HPP
