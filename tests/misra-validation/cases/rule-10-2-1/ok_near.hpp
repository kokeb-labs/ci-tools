// Near misses (near): fixed types on opaque and member enumerations.
#ifndef KV_RULE_10_2_1_OK_NEAR_HPP
#define KV_RULE_10_2_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_10_2_1::ok_near {

enum class Phase : std::uint8_t;
enum class Phase : std::uint8_t { kA, kB };

class Motor {
 public:
  enum class State : std::uint8_t { kOff, kOn };
  State state() const { return state_; }
  Phase phase() const { return phase_; }

 private:
  State state_ = State::kOff;
  Phase phase_ = Phase::kA;
};

}  // namespace kv::rule_10_2_1::ok_near

#endif  // KV_RULE_10_2_1_OK_NEAR_HPP
