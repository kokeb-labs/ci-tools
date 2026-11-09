// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_0_2_3_OK_NEAR_HPP
#define KV_RULE_0_2_3_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_0_2_3::near {

class Reader {
 public:
  [[nodiscard]] std::uint32_t get() const { return decode().value; }

 private:
  // The private type is used only as the return type of a private function that is called.
  struct Decoded {
    std::uint32_t value;
  };
  [[nodiscard]] Decoded decode() const { return Decoded{raw_ & 0xFFU}; }
  std::uint32_t raw_{0U};
};

inline std::uint32_t local_type(std::uint32_t v) {
  struct Pair {
    std::uint32_t lo;
    std::uint32_t hi;
  };
  const Pair p{v & 0xFFFFU, v >> 16U};
  return p.lo ^ p.hi;
}

}  // namespace kv::rule_0_2_3::near

#endif  // KV_RULE_0_2_3_OK_NEAR_HPP
