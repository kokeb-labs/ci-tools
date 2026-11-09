// Seeded violation: the handler of a constructor's function-try-block uses a non-static member.
namespace kv::rule_18_3_3::bad {

class Port {
 public:
  Port() try : id_(1) {  // seeded: clang
  } catch (...) {  // seeded: gcc
    id_ = 0;
  }

 private:
  int id_;
};

}  // namespace kv::rule_18_3_3::bad
