// Compliant: only the chosen operand of ?: is evaluated, after the condition, and each writes `reply`
// once; && evaluates its left operand (which writes `failure`) before its right operand (which reads it).
#ifndef KV_RULE_4_6_1_SEQUENCED_OK_HPP
#define KV_RULE_4_6_1_SEQUENCED_OK_HPP

#include <cstdint>

namespace kv::rule_4_6_1_sequenced::ok {

enum class Failure : std::uint8_t { kOther, kNack };

struct Reply {
  std::uint8_t status;
};

template <typename Bus>
class Driver {
 public:
  explicit Driver(Bus& bus) : bus_(bus) {}
  bool Write(bool fast, std::uint8_t mask);

 private:
  static constexpr std::uint8_t kStatus = 0U;
  Bus& bus_;
};

template <typename Bus>
bool Driver<Bus>::Write(bool fast, std::uint8_t mask) {
  Reply reply{};
  const bool ok = fast ? bus_.Data8(mask, reply) : bus_.Write8(kStatus, mask, reply);
  return ok && (reply.status != 0xFFU);
}

template <typename Port>
bool Nacked(Port& port) {
  Failure failure = Failure::kOther;
  return port.GetLastFailure(failure) && (failure == Failure::kNack);
}

class FakeBus {
 public:
  bool Data8(std::uint8_t value, Reply& reply) {
    reply = Reply{value};
    return ok_;
  }
  bool Write8(std::uint8_t bank, std::uint8_t value, Reply& reply) {
    reply = Reply{static_cast<std::uint8_t>(static_cast<std::uint32_t>(bank) | static_cast<std::uint32_t>(value))};
    return ok_;
  }
  bool GetLastFailure(Failure& failure) {
    failure = last_;
    return ok_;
  }

 private:
  bool ok_ = true;
  Failure last_ = Failure::kNack;
};

inline bool Probe(FakeBus& bus, bool fast) {
  Driver<FakeBus> driver{bus};
  const bool written = driver.Write(fast, 0x0FU);
  const bool nacked = Nacked(bus);
  return written != nacked;
}

}  // namespace kv::rule_4_6_1_sequenced::ok

#endif  // KV_RULE_4_6_1_SEQUENCED_OK_HPP
