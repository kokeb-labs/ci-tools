// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_2_5_OK_NEAR_HPP
#define KV_RULE_8_2_5_OK_NEAR_HPP

#include <bit>
#include <cstdint>

namespace kv::rule_8_2_5::ok_near {

struct Base {
  std::uint32_t id{0U};
};

struct Child : Base {
  std::uint32_t extra{0U};
};

inline std::uint32_t id_of(Child const& c) { return (c.extra == 0U) ? static_cast<Base const&>(c).id : c.extra; }

inline std::uint64_t bits(double d) { return std::bit_cast<std::uint64_t>(d); }

}  // namespace kv::rule_8_2_5::ok_near

#endif  // KV_RULE_8_2_5_OK_NEAR_HPP
