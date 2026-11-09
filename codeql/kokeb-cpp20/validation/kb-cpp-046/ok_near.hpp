// Near misses of KB-CPP-046: names that only contain Result are not Result types.
#ifndef KV_KB_CPP_046_OK_NEAR_HPP
#define KV_KB_CPP_046_OK_NEAR_HPP

#include <cstdint>

namespace kv::kb_cpp_046::ok_near {

struct SensorResult {
  std::uint16_t raw{0U};
};

struct ResultSink {
  std::uint8_t count{0U};
};

class Driver {
 public:
  class [[nodiscard]] Result {
   public:
    std::uint8_t code{0U};
  };

  [[nodiscard]] static Result read() { return Result{}; }
};

[[nodiscard]] inline bool used(const SensorResult& s, const ResultSink& k) {
  return (s.raw != 0U) || (k.count != 0U) || (Driver::read().code != 0U);
}

}  // namespace kv::kb_cpp_046::ok_near

#endif  // KV_KB_CPP_046_OK_NEAR_HPP
